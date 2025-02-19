import click
from loguru import logger
from typing import Dict, Any, List, Optional
import pathlib
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from .approval_system import ApprovalSystem, ValidationResult
from .checkpoint_system import CheckpointSystem
from .base_agent import BaseAgent
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

class ProductManager(BaseAgent):
    """Product Manager agent responsible for creating and managing product specifications."""
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Product Manager with approval and checkpoint systems."""
        super().__init__(model)  # Initialize BaseAgent
        
        # Initialize systems
        self.approval_system = ApprovalSystem(model)
        self.checkpoint_system = CheckpointSystem(self.approval_system)

    async def analyze_market_context(self, prompt: str) -> str:
        """Analyze market context from the user prompt."""
        try:
            system_message = """Analyze the market context for this product. Return a JSON object with:
            - target_market: Primary target market
            - competitors: List of key competitors
            - trends: List of relevant market trends
            - demographics: Target user demographics
            - pain_points: List of user pain points
            - opportunities: List of market opportunities"""
            
            logger.debug(f"[Market Analysis] Sending prompt: {prompt[:100]}...")
            response = await self.get_completion(prompt, system_message)
            logger.debug(f"[Market Analysis] Response type: {type(response)}")
            logger.debug(f"[Market Analysis] Raw response: {response[:200]}...")
            
            # Validate JSON structure before returning
            try:
                parsed = json.loads(response)
                logger.debug(f"[Market Analysis] Parsed structure: {type(parsed)}")
                logger.debug(f"[Market Analysis] Available keys: {parsed.keys() if isinstance(parsed, dict) else 'Not a dict'}")
                return response
            except json.JSONDecodeError as e:
                logger.error(f"[Market Analysis] JSON validation failed: {str(e)}")
                logger.error(f"[Market Analysis] Invalid JSON response: {response}")
                raise ValueError(f"Invalid JSON response from market analysis: {str(e)}")
            
        except Exception as e:
            logger.error(f"[Market Analysis] Error analyzing market context: {str(e)}")
            raise

    async def generate_user_personas(self, prompt: str) -> str:
        """Create user personas based on market context."""
        try:
            system_message = """Generate user personas for this product. Return a JSON array of personas, each with:
            - name: Persona name
            - role: Professional role
            - goals: List of goals
            - challenges: List of challenges
            - preferences: List of preferences
            - tech_proficiency: Technical proficiency level"""
            
            logger.debug(f"[Personas] Full prompt: {prompt}")
            logger.debug(f"[Personas] System message: {system_message}")
            
            response = await self.get_completion(prompt, system_message)
            
            # Enhanced response inspection
            logger.debug(f"[Personas] Raw response type: {type(response)}")
            logger.debug(f"[Personas] Raw response: {response[:500]}")
            
            # Validate JSON structure
            try:
                parsed = json.loads(response)
                logger.debug(f"[Personas] Parsed type: {type(parsed)}")
                logger.debug(f"[Personas] Parsed structure: {json.dumps(parsed, indent=2)[:500]}")
                
                if not isinstance(parsed, list):
                    logger.error(f"[Personas] Expected list but got {type(parsed)}")
                    raise ValueError(f"Invalid personas response format: expected list but got {type(parsed)}")
                
                for idx, persona in enumerate(parsed):
                    logger.debug(f"[Personas] Validating persona {idx}")
                    logger.debug(f"[Personas] Persona keys: {persona.keys() if isinstance(persona, dict) else 'Not a dict'}")
                    
                    required_fields = {'name', 'role', 'goals', 'challenges', 'preferences', 'tech_proficiency'}
                    if isinstance(persona, dict):
                        missing_fields = required_fields - set(persona.keys())
                        if missing_fields:
                            logger.error(f"[Personas] Missing required fields in persona {idx}: {missing_fields}")
                
                return response
                
            except json.JSONDecodeError as e:
                logger.error(f"[Personas] JSON parsing failed: {str(e)}")
                logger.error(f"[Personas] Invalid JSON: {response}")
                raise ValueError(f"Invalid JSON in personas response: {str(e)}")
            
        except Exception as e:
            logger.error(f"[Personas] Error generating personas: {str(e)}")
            raise

    async def define_features(self, prompt: str) -> str:
        """Define product features based on requirements and user personas."""
        try:
            system_message = """Define product features based on requirements. Return a JSON array of features, each with:
            - name: Feature name
            - description: Feature description
            - priority: Priority level (high/medium/low)
            - requirements: List of requirements
            - acceptance_criteria: List of acceptance criteria
            Optional fields:
            - technical_requirements: List of technical requirements
            - dependencies: List of dependencies
            - estimated_effort: Effort estimate
            - risks: List of potential risks"""
            
            logger.debug(f"[Features] Sending prompt: {prompt[:100]}...")
            response = await self.get_completion(prompt, system_message)
            logger.debug(f"[Features] Response type: {type(response)}")
            logger.debug(f"[Features] Raw response: {response[:200]}...")
            
            # Create mock response object to match expected structure
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            
            # Validate JSON structure
            try:
                parsed = json.loads(response)
                logger.debug(f"[Features] Parsed structure: {type(parsed)}")
                if isinstance(parsed, list):
                    logger.debug(f"[Features] First feature keys: {parsed[0].keys() if parsed else 'Empty list'}")
                    logger.debug(f"[Features] First feature types: {[(k, type(v)) for k, v in parsed[0].items()] if parsed else 'Empty list'}")
                return MockResponse(response)
            except json.JSONDecodeError as e:
                logger.error(f"[Features] JSON validation failed: {str(e)}")
                logger.error(f"[Features] Invalid JSON response: {response}")
                raise ValueError(f"Invalid JSON response for features: {str(e)}")
            
        except Exception as e:
            logger.error(f"[Features] Error defining features: {str(e)}")
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
        """Create product specifications based on user prompt."""
        try:
            # Get market context
            market_context_response = await self.analyze_market_context(prompt)
            logger.debug(f"[Response Format] Market context raw response type: {type(market_context_response)}")
            logger.debug(f"[Response Format] Market context raw response structure: {market_context_response}")
            
            try:
                market_data = json.loads(market_context_response)
                logger.debug(f"[Data Structure] Parsed market data keys: {market_data.keys() if isinstance(market_data, dict) else 'Not a dict'}")
                logger.debug(f"[Data Structure] Market data types: {[(k, type(v)) for k, v in market_data.items() if isinstance(market_data, dict)]}")
            except json.JSONDecodeError as e:
                logger.error(f"[Response Format] JSON parsing failed for market context: {str(e)}")
                raise
            
            # Log pre-validation data
            logger.debug(f"[Model Validation] Pre-validation market data: {market_data}")
            try:
                market_context = MarketContext.model_validate(market_data)
                logger.debug(f"[Model Validation] Successful market context validation: {market_context}")
            except Exception as e:
                logger.error(f"[Model Validation] Market context validation failed: {str(e)}")
                raise
            
            # Get user personas
            personas_response = await self.generate_user_personas(prompt)
            logger.debug(f"[Response Format] Raw personas response type: {type(personas_response)}")
            logger.debug(f"[Response Format] Raw personas response: {personas_response}")
            
            try:
                personas_data = json.loads(personas_response)
                logger.debug(f"[Data Structure] Parsed personas data type: {type(personas_data)}")
                logger.debug(f"[Data Structure] First persona keys (if list): {personas_data[0].keys() if isinstance(personas_data, list) and len(personas_data) > 0 else 'No personas'}")
            except Exception as e:
                logger.error(f"[Response Format] Personas parsing failed: {str(e)}")
                raise
            
            try:
                personas = [UserPersona.model_validate(persona) for persona in personas_data]
                logger.debug(f"[Model Validation] Successfully validated {len(personas)} personas")
            except Exception as e:
                logger.error(f"[Model Validation] Persona validation failed: {str(e)}")
                raise
            
            # Get features
            features_response = await self.define_features(prompt)
            logger.debug(f"[Response Format] Raw features response type: {type(features_response)}")
            logger.debug(f"[Response Format] Raw features structure: {features_response}")
            
            try:
                features_data = json.loads(features_response.text)
                logger.debug(f"[Data Structure] Parsed features data type: {type(features_data)}")
                if isinstance(features_data, list) and features_data:
                    logger.debug(f"[Data Structure] Sample feature keys: {features_data[0].keys()}")
                    logger.debug(f"[Data Structure] Sample feature types: {[(k, type(v)) for k, v in features_data[0].items()]}")
            except Exception as e:
                logger.error(f"[Response Format] Features parsing failed: {str(e)}")
                raise
            
            try:
                features = [FeatureSpecification.model_validate(feature) for feature in features_data]
                logger.debug(f"[Model Validation] Successfully validated {len(features)} features")
            except Exception as e:
                logger.error(f"[Model Validation] Feature validation failed: {str(e)}")
                raise
            
            # Create final specification
            spec = ProductSpecification(
                title="AI Task Manager",
                description="Task management with AI prioritization",
                market_context=market_context,
                audience=personas,
                features=features
            )
            
            return spec
            
        except Exception as e:
            logger.error(f"[Critical] Error creating product specifications: {str(e)}")
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
