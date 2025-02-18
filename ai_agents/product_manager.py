import click
from loguru import logger
from typing import Dict, Any, List, Optional
import pathlib
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from .approval_system import ApprovalSystem, ValidationResult
from .checkpoint_system import CheckpointSystem
import json
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

class MarketContext(BaseModel):
    """Model for market context."""
    target_market: str
    competitors: List[str]
    trends: List[str]
    demographics: str
    pain_points: List[str]
    opportunities: List[str]

class UserPersona(BaseModel):
    """Model for user personas."""
    name: str
    role: str
    goals: List[str]
    challenges: List[str]
    preferences: List[str]
    tech_proficiency: str

class FeatureSpecification(BaseModel):
    """Model for feature specifications."""
    name: str
    description: str
    priority: str
    requirements: List[str]
    acceptance_criteria: List[str]
    
    # Optional fields
    technical_requirements: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    estimated_effort: Optional[str] = None
    risks: Optional[List[str]] = None

class ProductSpecification(BaseModel):
    """Model for product specifications."""
    title: str
    description: str
    market_context: MarketContext
    audience: List[UserPersona]
    features: List[FeatureSpecification]
    success_metrics: Optional[Dict[str, List[str]]] = None
    technical_requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    timeline: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, List[str]]] = None
    risks_and_mitigations: Optional[Dict[str, List[str]]] = None
    assumptions: Optional[List[str]] = None
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
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize systems
        self.approval_system = ApprovalSystem(model)
        self.checkpoint_system = CheckpointSystem(self.approval_system)
        
    async def analyze_market_context(self, prompt: str) -> str:
        """Analyze market context from the user prompt."""
        logger.info(f"Analyzing market context for prompt: {prompt[:100]}...")
        
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

        try:
            response = await self.client.generate_content(context_prompt)
            logger.debug(f"Raw Gemini response type: {type(response)}")
            logger.debug(f"Raw Gemini response attributes: {dir(response)}")
            logger.debug(f"Raw Gemini response: {response}")
            
            # Handle response correctly based on type
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")
                
        except Exception as e:
            logger.error(f"Error analyzing market context: {str(e)}")
            raise

    async def create_user_personas(self, market_context: str) -> List[UserPersona]:
        """Create user personas based on market context."""
        logger.info("Creating user personas from market context...")
        logger.debug(f"Market context input: {market_context[:100]}...")
        
        try:
            personas_data = json.loads(market_context)
            logger.debug(f"Parsed personas data type: {type(personas_data)}")
            logger.debug(f"Parsed personas data: {personas_data}")
            
            if isinstance(personas_data, list):
                personas = []
                for persona in personas_data:
                    try:
                        personas.append(UserPersona.model_validate(persona))
                    except ValidationError as e:
                        logger.error(f"Validation error for persona: {str(e)}")
                        logger.debug(f"Failed to validate persona: {persona}")
                return personas
            elif isinstance(personas_data, dict):
                try:
                    return [UserPersona.model_validate(personas_data)]
                except ValidationError as e:
                    logger.error(f"Validation error for persona: {str(e)}")
                    logger.debug(f"Failed to validate persona: {personas_data}")
                    raise
            else:
                raise ValueError(f"Unexpected personas data type: {type(personas_data)}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.debug(f"Failed to parse JSON: {market_context}")
            raise
        except Exception as e:
            logger.error(f"Error creating user personas: {str(e)}")
            raise

    async def define_features(self, 
                            prompt: str, 
                            market_context: str,
                            personas: List[UserPersona]) -> List[FeatureSpecification]:
        """Define product features based on requirements and user personas."""
        try:
            feature_prompt = f"""Define product features based on these inputs:

            Requirements:
            {prompt}

            Market Context:
            {market_context}

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
            features = []
            for feature in features_data:
                try:
                    features.append(FeatureSpecification.model_validate(feature))
                except ValidationError as e:
                    logger.error(f"Validation error for feature: {str(e)}")
                    logger.debug(f"Failed to validate feature: {feature}")
            return features

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
        """Create product specifications from user prompt."""
        try:
            # Step 1: Analyze market context
            market_context = await self.analyze_market_context(prompt)
            logger.debug(f"Market context type: {type(market_context)}")
            logger.debug(f"Market context raw: {market_context}")
            
            try:
                market_data = json.loads(market_context) if isinstance(market_context, str) else market_context
                logger.debug(f"Parsed market data: {market_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse market context as JSON: {e}")
                raise
            
            # Step 2: Create user personas
            personas_prompt = f"""Create detailed user personas based on this market context:

            Market Context:
            {market_context}

            For each major user segment, create a persona that includes:
            1. Name and role
            2. Goals and objectives
            3. Key challenges
            4. User preferences
            5. Technical proficiency level

            Format the response as a JSON array of UserPersona objects.
            """
            
            response = await self.client.generate_content(personas_prompt)
            logger.debug(f"Raw personas response: {response}")
            logger.debug(f"Personas response type: {type(response)}")
            logger.debug(f"Personas response text type: {type(response.text)}")
            
            try:
                personas_data = json.loads(response.text)
                logger.debug(f"Parsed personas data: {personas_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse personas response as JSON: {e}")
                raise
                
            try:
                personas = [UserPersona.model_validate(persona) for persona in personas_data]
                logger.debug(f"Validated personas: {personas}")
            except ValidationError as e:
                logger.error(f"Failed to validate personas: {e}")
                raise
            
            # Step 3: Define features
            features = await self.define_features(prompt, market_context, personas)
            logger.debug(f"Generated features: {features}")
            
            # Step 4: Generate final specification
            spec_prompt = f"""Create a comprehensive product specification based on:

            Project Requirements:
            {prompt}

            Market Context:
            {market_context}

            User Personas:
            {json.dumps([persona.model_dump() for persona in personas], indent=2)}

            Features:
            {json.dumps([feature.model_dump() for feature in features], indent=2)}

            Format the response as a ProductSpecification object.
            """
            
            response = await self.client.generate_content(spec_prompt)
            logger.debug(f"Raw spec response: {response}")
            logger.debug(f"Spec response type: {type(response)}")
            
            try:
                spec_data = json.loads(response.text)
                logger.debug(f"Parsed spec data: {spec_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse spec response as JSON: {e}")
                raise
            
            try:
                # Create specification object with validated components
                spec = ProductSpecification(
                    title=spec_data["title"],
                    description=spec_data["description"],
                    market_context=MarketContext.model_validate(spec_data["market_context"]),
                    audience=personas,
                    features=[FeatureSpecification.model_validate(feature) for feature in spec_data.get("features", [])]
                )
                logger.debug(f"Created spec object: {spec}")
            except ValidationError as e:
                logger.error(f"Failed to create ProductSpecification: {e}")
                logger.debug(f"Spec data used: {spec_data}")
                raise
            
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
{specs.market_context.target_market}

### Competitors
{chr(10).join(f'- {comp}' for comp in specs.market_context.competitors)}

### Market Trends
{chr(10).join(f'- {trend}' for trend in specs.market_context.trends)}

### User Demographics
{specs.market_context.demographics}

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
{chr(10).join(f'- {pref}' for pref in persona.preferences)}

**Technical Proficiency:** {persona.tech_proficiency}
''' for persona in specs.audience])}

## Features
{chr(10).join([f'''
### {feature.name}
**Priority:** {feature.priority}

**Description:**
{feature.description}

**Requirements:**
{chr(10).join(f'- {req}' for req in feature.requirements)}

**Acceptance Criteria:**
{chr(10).join(f'- {criteria}' for criteria in feature.acceptance_criteria)}

**Technical Requirements:**
{chr(10).join(f'- {req}' for req in feature.technical_requirements) if feature.technical_requirements else ''}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in feature.dependencies) if feature.dependencies else ''}

**Estimated Effort:** {feature.estimated_effort if feature.estimated_effort else ''}

**Risks:**
{chr(10).join(f'- {risk}' for risk in feature.risks) if feature.risks else ''}
''' for feature in specs.features])}

## Success Metrics
{chr(10).join([f'''
### {category}
{chr(10).join(f'- {metric}' for metric in metrics)}
''' for category, metrics in specs.success_metrics.items()]) if specs.success_metrics else ''}

## Technical Requirements
{chr(10).join(f'- {req}' for req in specs.technical_requirements) if specs.technical_requirements else ''}

## Constraints
{chr(10).join(f'- {constraint}' for constraint in specs.constraints) if specs.constraints else ''}

## Timeline
{chr(10).join(f'- {phase}: {details}' for phase, details in specs.timeline.items()) if specs.timeline else ''}

## Dependencies
{chr(10).join([f'''
### {category}
{chr(10).join(f'- {dep}' for dep in deps)}
''' for category, deps in specs.dependencies.items()]) if specs.dependencies else ''}

## Risks and Mitigations
{chr(10).join([f'''
### {risk_category}
{chr(10).join(f'- {strategy}' for strategy in strategies)}
''' for risk_category, strategies in specs.risks_and_mitigations.items()]) if specs.risks_and_mitigations else ''}

## Assumptions
{chr(10).join(f'- {assumption}' for assumption in specs.assumptions) if specs.assumptions else ''}

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
