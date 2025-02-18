import click
from loguru import logger
from typing import Dict, Any, List, Optional
import pathlib
from datetime import datetime
from pydantic import BaseModel, Field
from .approval_system import ApprovalSystem, ValidationResult
from .checkpoint_system import CheckpointSystem
import json
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

class MarketContext(BaseModel):
    target_market: List[str]
    competitors: List[Dict[str, Any]]
    market_trends: List[str]
    user_demographics: Dict[str, Any]
    pain_points: List[str]
    opportunities: List[str]

class UserPersona(BaseModel):
    name: str
    role: str
    goals: List[str]
    challenges: List[str]
    preferences: Dict[str, Any]
    technical_proficiency: str

class FeatureSpecification(BaseModel):
    name: str
    description: str
    priority: str
    user_stories: List[str]
    acceptance_criteria: List[str]
    technical_requirements: List[str]
    dependencies: List[str]
    estimated_effort: str
    risks: List[str]

class ProductSpecification(BaseModel):
    """Product specification model with enhanced validation."""
    title: str
    description: str
    version: str = Field(default_factory=lambda: datetime.now().strftime("%Y.%m.%d"))
    scope: Dict[str, Any]
    audience: List[UserPersona]
    market_context: MarketContext
    features: List[FeatureSpecification]
    success_metrics: Dict[str, List[str]]
    technical_requirements: List[str]
    constraints: List[str]
    timeline: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    risks_and_mitigations: Dict[str, List[str]]
    assumptions: List[str]
    validation_status: Dict[str, ValidationResult] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    session_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))

class ProductManager:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Product Manager with approval and checkpoint systems."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize systems
        self.approval_system = ApprovalSystem(model)
        self.checkpoint_system = CheckpointSystem(self.approval_system)
        
    async def analyze_market_context(self, prompt: str) -> MarketContext:
        """Analyze market context from the user prompt."""
        try:
            context_prompt = f"""Analyze the following project requirements and generate a detailed market context:

            Project Requirements:
            {prompt}

            Generate a comprehensive market analysis including:
            1. Target market segments
            2. Key competitors and their offerings
            3. Current market trends
            4. User demographics
            5. Pain points and challenges
            6. Market opportunities

            Format the response as a JSON object matching the MarketContext model.
            """

            response = await self.client.generate_content(context_prompt)
            context_data = json.loads(response.text)
            return MarketContext(**context_data)

        except Exception as e:
            logger.error(f"Error analyzing market context: {str(e)}")
            raise

    async def create_user_personas(self, market_context: MarketContext) -> List[UserPersona]:
        """Generate user personas based on market context."""
        try:
            persona_prompt = f"""Create detailed user personas based on this market context:

            Market Context:
            {json.dumps(market_context.model_dump(), indent=2)}

            For each major user segment, create a persona that includes:
            1. Name and role
            2. Goals and objectives
            3. Key challenges
            4. User preferences
            5. Technical proficiency level

            Format the response as a JSON array of UserPersona objects.
            """

            response = await self.client.generate_content(persona_prompt)
            personas_data = json.loads(response.text)
            return [UserPersona.parse_obj(persona) for persona in personas_data]

        except Exception as e:
            logger.error(f"Error creating user personas: {str(e)}")
            raise

    async def define_features(self, 
                            prompt: str, 
                            market_context: MarketContext,
                            personas: List[UserPersona]) -> List[FeatureSpecification]:
        """Define product features based on requirements and user personas."""
        try:
            feature_prompt = f"""Define product features based on these inputs:

            Requirements:
            {prompt}

            Market Context:
            {json.dumps(market_context.model_dump(), indent=2)}

            User Personas:
            {json.dumps([persona.model_dump() for persona in personas], indent=2)}

            For each major feature:
            1. Provide detailed description and priority
            2. Create user stories from persona perspectives
            3. Define clear acceptance criteria
            4. Specify technical requirements
            5. Identify dependencies and risks
            6. Estimate implementation effort

            Format the response as a JSON array of FeatureSpecification objects.
            """

            response = await self.client.generate_content(feature_prompt)
            features_data = json.loads(response.text)
            return [FeatureSpecification(**feature) for feature in features_data]

        except Exception as e:
            logger.error(f"Error defining features: {str(e)}")
            raise

    async def validate_with_stakeholders(self, 
                                      spec: ProductSpecification,
                                      roles: List[str]) -> Dict[str, ValidationResult]:
        """Cross-validate specifications with different stakeholder roles."""
        try:
            validation_results = {}
            
            for role in roles:
                checkpoint_id = f"spec_validation_{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                checkpoint = self.checkpoint_system.create_checkpoint(checkpoint_id, f"{role}_validation")
                
                validation = await self.approval_system.validate_specifications(
                    spec.model_dump(),
                    role,
                    {
                        "market_context": spec.market_context.model_dump(),
                        "user_personas": [persona.model_dump() for persona in spec.audience],
                        "features": [feature.model_dump() for feature in spec.features]
                    }
                )
                
                if validation.is_approved:
                    self.checkpoint_system.approve_checkpoint(
                        checkpoint_id,
                        validation,
                        approved_by=[role]
                    )
                else:
                    self.checkpoint_system.reject_checkpoint(
                        checkpoint_id,
                        validation,
                        blocking_issues=validation.issues
                    )
                
                validation_results[role] = validation
            
            return validation_results

        except Exception as e:
            logger.error(f"Error in stakeholder validation: {str(e)}")
            raise

    async def create_product_specs(self, prompt: str) -> ProductSpecification:
        """Create comprehensive product specifications from user prompt with automated validation."""
        try:
            # Generate market context and user personas
            market_context = await self.analyze_market_context(prompt)
            personas = await self.create_user_personas(market_context)
            features = await self.define_features(prompt, market_context, personas)

            # Generate initial specification
            spec_prompt = f"""Create detailed product specifications based on:

            Original Requirements:
            {prompt}

            Market Context:
            {json.dumps(market_context.model_dump(), indent=2)}

            User Personas:
            {json.dumps([persona.model_dump() for persona in personas], indent=2)}

            Features:
            {json.dumps([feature.model_dump() for feature in features], indent=2)}

            Include:
            1. Clear scope definition
            2. Success metrics for each objective
            3. Technical requirements and constraints
            4. Project timeline and milestones
            5. Dependencies and assumptions
            6. Risk assessment and mitigation strategies

            Format as a JSON object matching the ProductSpecification model.
            """

            response = await self.client.generate_content(spec_prompt)
            spec_data = json.loads(response.text)
            
            # Create specification object
            spec = ProductSpecification(
                **spec_data,
                market_context=market_context,
                audience=personas,
                features=features
            )

            # Cross-validate with stakeholders
            validation_results = await self.validate_with_stakeholders(
                spec,
                ["architect", "engineer", "qa_engineer", "security_analyst"]
            )
            
            # Update specification with validation results
            spec.validation_status = validation_results

            return spec

        except Exception as e:
            logger.error(f"Error creating product specifications: {str(e)}")
            raise

    async def generate_specifications(self, prompt: str) -> ProductSpecification:
        """Wrapper method for integration test compatibility."""
        try:
            specs = await self.create_product_specs(prompt)
            return specs
        except Exception as e:
            logger.error(f"Error generating specifications: {str(e)}")
            raise

    def save_specs(self, specs: ProductSpecification, output_file: str):
        """Save product specifications to a markdown file."""
        try:
            output_path = pathlib.Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            markdown_content = f"""# Product Specifications
Version: {specs.version}
Session ID: {specs.session_id}
Last Updated: {specs.last_updated.strftime('%Y-%m-%d %H:%M:%S')}

## Overview
**Title:** {specs.title}

**Description:**
{specs.description}

## Market Context
### Target Market
{chr(10).join(f'- {market}' for market in specs.market_context.target_market)}

### Competitors
{chr(10).join([f'''
#### {comp['name']}
- Strengths: {', '.join(comp.get('strengths', []))}
- Weaknesses: {', '.join(comp.get('weaknesses', []))}
- Market Position: {comp.get('market_position', 'N/A')}
''' for comp in specs.market_context.competitors])}

### Market Trends
{chr(10).join(f'- {trend}' for trend in specs.market_context.market_trends)}

### User Demographics
{chr(10).join(f'- {key}: {value}' for key, value in specs.market_context.user_demographics.items())}

### Pain Points
{chr(10).join(f'- {point}' for point in specs.market_context.pain_points)}

### Opportunities
{chr(10).join(f'- {opp}' for opp in specs.market_context.opportunities)}

## User Personas
{chr(10).join([f'''
### {persona.name} ({persona.role})
**Goals:**
{chr(10).join(f'- {goal}' for goal in persona.goals)}

**Challenges:**
{chr(10).join(f'- {challenge}' for challenge in persona.challenges)}

**Preferences:**
{chr(10).join(f'- {key}: {value}' for key, value in persona.preferences.items())}

**Technical Proficiency:** {persona.technical_proficiency}
''' for persona in specs.audience])}

## Features
{chr(10).join([f'''
### {feature.name}
**Priority:** {feature.priority}

**Description:**
{feature.description}

**User Stories:**
{chr(10).join(f'- {story}' for story in feature.user_stories)}

**Acceptance Criteria:**
{chr(10).join(f'- {criteria}' for criteria in feature.acceptance_criteria)}

**Technical Requirements:**
{chr(10).join(f'- {req}' for req in feature.technical_requirements)}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in feature.dependencies)}

**Estimated Effort:** {feature.estimated_effort}

**Risks:**
{chr(10).join(f'- {risk}' for risk in feature.risks)}
''' for feature in specs.features])}

## Success Metrics
{chr(10).join([f'''
### {category}
{chr(10).join(f'- {metric}' for metric in metrics)}
''' for category, metrics in specs.success_metrics.items()])}

## Technical Requirements
{chr(10).join(f'- {req}' for req in specs.technical_requirements)}

## Constraints
{chr(10).join(f'- {constraint}' for constraint in specs.constraints)}

## Timeline
{chr(10).join(f'- {phase}: {details}' for phase, details in specs.timeline.items())}

## Dependencies
{chr(10).join([f'''
### {category}
{chr(10).join(f'- {dep}' for dep in deps)}
''' for category, deps in specs.dependencies.items()])}

## Risks and Mitigations
{chr(10).join([f'''
### {risk_category}
{chr(10).join(f'- {strategy}' for strategy in strategies)}
''' for risk_category, strategies in specs.risks_and_mitigations.items()])}

## Assumptions
{chr(10).join(f'- {assumption}' for assumption in specs.assumptions)}

## Validation Status
{chr(10).join([f'''
### {role} Validation
**Status:** {'✅ Approved' if result.is_approved else '❌ Rejected'}

**Issues:**
{chr(10).join(f'- {issue}' for issue in result.issues)}

**Suggestions:**
{chr(10).join(f'- {suggestion}' for suggestion in result.suggestions)}
''' for role, result in specs.validation_status.items()])}
"""

            with output_path.open('w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Product specifications saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving specifications: {str(e)}")
            raise

@click.command()
@click.argument('output', type=click.Path())
@click.option('--context-file', type=click.Path(exists=True), help='Optional JSON file with additional context')
async def main(output: str, context_file: Optional[str] = None):
    """Generate product specifications using the Product Manager agent."""
    try:
        # Get user input
        prompt = click.prompt("Please describe your product requirements", type=str)
        
        # Load additional context if provided
        context = {}
        if context_file:
            with open(context_file, 'r') as f:
                context = json.load(f)
        
        # Initialize product manager and generate specs
        manager = ProductManager()
        specs = await manager.create_product_specs(prompt)
        
        # Save specifications
        manager.save_specs(specs, output)
        
        click.echo(f"Product specifications have been generated and saved to {output}")
        
    except Exception as e:
        logger.error(f"Error in specification generation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
