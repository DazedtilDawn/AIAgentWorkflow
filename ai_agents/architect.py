import click
from loguru import logger
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pathlib
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime

class TechStack(BaseModel):
    frontend: List[str]
    backend: List[str]
    database: List[str]
    infrastructure: List[str]
    tools_and_services: List[str]
    version_constraints: Optional[Dict[str, str]] = None
    integration_points: Optional[List[str]] = None

class Component(BaseModel):
    name: str
    description: str
    responsibilities: List[str]
    dependencies: List[str]
    technical_requirements: List[str]
    api_endpoints: Optional[List[Dict[str, Any]]] = None
    performance_requirements: Optional[Dict[str, str]] = None
    testing_strategy: Optional[List[str]] = None

class DataFlow(BaseModel):
    source: str
    destination: str
    description: str
    data_type: str
    frequency: str
    security_requirements: List[str]
    validation_rules: Optional[List[str]] = None
    error_handling: Optional[Dict[str, str]] = None
    monitoring_metrics: Optional[List[str]] = None

class SecurityMeasure(BaseModel):
    category: str
    measures: List[str]
    implementation_priority: str
    compliance_requirements: Optional[List[str]] = None
    threat_mitigations: Optional[Dict[str, List[str]]] = None

class DeploymentStage(BaseModel):
    name: str
    components: List[str]
    prerequisites: List[str]
    success_criteria: List[str]
    rollback_plan: List[str]
    monitoring_metrics: Optional[List[str]] = None
    automation_scripts: Optional[List[str]] = None
    environment_config: Optional[Dict[str, Any]] = None

class SystemArchitecture(BaseModel):
    overview: str
    components: List[Component]
    data_flows: List[DataFlow]
    tech_stack: TechStack
    security_measures: List[SecurityMeasure]
    deployment_strategy: List[DeploymentStage]
    design_patterns: List[str]
    scalability_considerations: List[str]
    monitoring_requirements: List[str]
    session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    api_documentation: Optional[Dict[str, Any]] = None
    performance_benchmarks: Optional[Dict[str, Any]] = None
    disaster_recovery_plan: Optional[Dict[str, Any]] = None

class Architect:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Architect with Gemini configuration."""
        self.model = model
        
        # Load environment variables and configure Gemini
        current_dir = pathlib.Path(__file__).parent.parent.absolute()
        env_path = current_dir / '.env'
        load_dotenv(dotenv_path=env_path)
        
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
    
    async def generate_tech_stack(self, 
                                product_specs: Dict[str, Any], 
                                brainstorm_outcome: Dict[str, Any]) -> TechStack:
        """Generate technology stack recommendations."""
        try:
            prompt = f"""Analyze the product specifications and brainstorm outcome to recommend a comprehensive technology stack.

            Product Specifications:
            {json.dumps(product_specs, indent=2)}

            Selected Solution Ideas:
            {json.dumps(brainstorm_outcome.get('ideas', []), indent=2)}

            Provide a detailed technology stack that:
            1. Aligns with the technical requirements
            2. Supports the proposed features and scalability needs
            3. Considers integration requirements
            4. Specifies version constraints where critical
            5. Identifies key integration points

            Format as JSON with fields matching the TechStack model.
            """

            response = await self.client.generate_content(prompt)
            tech_stack_data = json.loads(response.text)
            return TechStack(**tech_stack_data)

        except Exception as e:
            logger.error(f"Error generating tech stack: {str(e)}")
            raise

    async def generate_components(self, 
                                product_specs: Dict[str, Any], 
                                tech_stack: TechStack) -> List[Component]:
        """Generate component definitions with detailed specifications."""
        try:
            prompt = f"""Design the system components based on the product specifications and selected technology stack.

            Product Specifications:
            {json.dumps(product_specs, indent=2)}

            Technology Stack:
            {json.dumps(tech_stack.dict(), indent=2)}

            For each major feature or functional area, define a component that:
            1. Has clear responsibilities and boundaries
            2. Specifies its API endpoints and interfaces
            3. Includes performance requirements
            4. Defines testing strategies
            5. Lists dependencies and technical requirements

            Format as JSON array of Component objects.
            """

            response = await self.client.generate_content(prompt)
            components_data = json.loads(response.text)
            return [Component(**comp) for comp in components_data]

        except Exception as e:
            logger.error(f"Error generating components: {str(e)}")
            raise

    async def generate_data_flows(self, 
                                components: List[Component], 
                                tech_stack: TechStack) -> List[DataFlow]:
        """Generate data flow specifications between components."""
        try:
            prompt = f"""Define the data flows between system components.

            Components:
            {json.dumps([comp.dict() for comp in components], indent=2)}

            Technology Stack:
            {json.dumps(tech_stack.dict(), indent=2)}

            For each significant interaction between components, specify:
            1. Data flow details and types
            2. Security requirements
            3. Validation rules
            4. Error handling strategies
            5. Monitoring metrics

            Format as JSON array of DataFlow objects.
            """

            response = await self.client.generate_content(prompt)
            flows_data = json.loads(response.text)
            return [DataFlow(**flow) for flow in flows_data]

        except Exception as e:
            logger.error(f"Error generating data flows: {str(e)}")
            raise

    async def generate_security_measures(self, 
                                      components: List[Component], 
                                      data_flows: List[DataFlow]) -> List[SecurityMeasure]:
        """Generate comprehensive security measures."""
        try:
            prompt = f"""Define security measures for the system components and data flows.

            Components:
            {json.dumps([comp.dict() for comp in components], indent=2)}

            Data Flows:
            {json.dumps([flow.dict() for flow in data_flows], indent=2)}

            For each security category, specify:
            1. Required security measures
            2. Implementation priorities
            3. Compliance requirements
            4. Threat mitigations
            5. Integration with existing security tools

            Format as JSON array of SecurityMeasure objects.
            """

            response = await self.client.generate_content(prompt)
            security_data = json.loads(response.text)
            return [SecurityMeasure(**measure) for measure in security_data]

        except Exception as e:
            logger.error(f"Error generating security measures: {str(e)}")
            raise

    async def generate_deployment_strategy(self, 
                                        components: List[Component], 
                                        tech_stack: TechStack) -> List[DeploymentStage]:
        """Generate deployment strategy with stages and automation."""
        try:
            prompt = f"""Define a comprehensive deployment strategy.

            Components:
            {json.dumps([comp.dict() for comp in components], indent=2)}

            Technology Stack:
            {json.dumps(tech_stack.dict(), indent=2)}

            For each deployment stage, specify:
            1. Required components and order
            2. Prerequisites and dependencies
            3. Success criteria and validation
            4. Rollback procedures
            5. Monitoring metrics
            6. Automation scripts
            7. Environment configurations

            Format as JSON array of DeploymentStage objects.
            """

            response = await self.client.generate_content(prompt)
            stages_data = json.loads(response.text)
            return [DeploymentStage(**stage) for stage in stages_data]

        except Exception as e:
            logger.error(f"Error generating deployment strategy: {str(e)}")
            raise

    async def generate_architecture(self, 
                                  product_specs: str, 
                                  brainstorm_outcome: str) -> SystemArchitecture:
        """Generate comprehensive system architecture."""
        try:
            # Parse input JSON
            specs_data = json.loads(product_specs)
            outcome_data = json.loads(brainstorm_outcome)

            # Generate components in parallel
            tech_stack = await self.generate_tech_stack(specs_data, outcome_data)
            components = await self.generate_components(specs_data, tech_stack)
            
            # Generate flows and security measures
            data_flows = await self.generate_data_flows(components, tech_stack)
            security_measures = await self.generate_security_measures(components, data_flows)
            
            # Generate deployment strategy
            deployment_strategy = await self.generate_deployment_strategy(components, tech_stack)

            # Generate additional architecture aspects
            architecture_prompt = f"""Analyze the system components and provide:
            1. Overview of the architecture
            2. Recommended design patterns
            3. Scalability considerations
            4. Monitoring requirements
            5. API documentation structure
            6. Performance benchmarks
            7. Disaster recovery guidelines

            Format as JSON with fields:
            - overview: string
            - design_patterns: list of strings
            - scalability_considerations: list of strings
            - monitoring_requirements: list of strings
            - api_documentation: object
            - performance_benchmarks: object
            - disaster_recovery_plan: object
            """

            response = await self.client.generate_content(architecture_prompt)
            arch_data = json.loads(response.text)

            # Create and return complete architecture
            return SystemArchitecture(
                overview=arch_data["overview"],
                components=components,
                data_flows=data_flows,
                tech_stack=tech_stack,
                security_measures=security_measures,
                deployment_strategy=deployment_strategy,
                design_patterns=arch_data["design_patterns"],
                scalability_considerations=arch_data["scalability_considerations"],
                monitoring_requirements=arch_data["monitoring_requirements"],
                api_documentation=arch_data.get("api_documentation"),
                performance_benchmarks=arch_data.get("performance_benchmarks"),
                disaster_recovery_plan=arch_data.get("disaster_recovery_plan")
            )

        except Exception as e:
            logger.error(f"Error generating architecture: {str(e)}")
            raise

    async def design_system(self, specs_file: str, brainstorm_file: str) -> str:
        """Wrapper method for integration test compatibility."""
        # Read the content from files
        try:
            with open(specs_file, 'r', encoding='utf-8') as f:
                specs = f.read()
            with open(brainstorm_file, 'r', encoding='utf-8') as f:
                brainstorm = f.read()
            
            # Call the actual method
            architecture = await self.generate_architecture(specs, brainstorm)
            return architecture
            
        except Exception as e:
            logger.error(f"Error in design_system: {str(e)}")
            raise

    def save_architecture(self, architecture: SystemArchitecture, output_file: str):
        """Save the system architecture to a markdown file."""
        try:
            output_path = pathlib.Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            markdown_content = f"""# System Architecture
Session ID: {architecture.session_id}

## Overview
{architecture.overview}

## Technology Stack
### Frontend
{chr(10).join(f'- {tech}' for tech in architecture.tech_stack.frontend)}

### Backend
{chr(10).join(f'- {tech}' for tech in architecture.tech_stack.backend)}

### Database
{chr(10).join(f'- {tech}' for tech in architecture.tech_stack.database)}

### Infrastructure
{chr(10).join(f'- {tech}' for tech in architecture.tech_stack.infrastructure)}

### Tools and Services
{chr(10).join(f'- {tech}' for tech in architecture.tech_stack.tools_and_services)}

## Components
{chr(10).join([f'''
### {component.name}
{component.description}

**Responsibilities:**
{chr(10).join(f'- {resp}' for resp in component.responsibilities)}

**Technical Requirements:**
{chr(10).join(f'- {req}' for req in component.technical_requirements)}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in component.dependencies)}

**API Endpoints:**
{json.dumps(component.api_endpoints, indent=2) if component.api_endpoints else "N/A"}

**Performance Requirements:**
{json.dumps(component.performance_requirements, indent=2) if component.performance_requirements else "N/A"}

**Testing Strategy:**
{chr(10).join(f'- {test}' for test in (component.testing_strategy or []))}
''' for component in architecture.components])}

## Data Flows
{chr(10).join([f'''
### {flow.source} → {flow.destination}
{flow.description}

- **Data Type:** {flow.data_type}
- **Frequency:** {flow.frequency}

**Security Requirements:**
{chr(10).join(f'- {req}' for req in flow.security_requirements)}

**Validation Rules:**
{chr(10).join(f'- {rule}' for rule in (flow.validation_rules or []))}

**Error Handling:**
{json.dumps(flow.error_handling, indent=2) if flow.error_handling else "N/A"}

**Monitoring Metrics:**
{chr(10).join(f'- {metric}' for metric in (flow.monitoring_metrics or []))}
''' for flow in architecture.data_flows])}

## Security Measures
{chr(10).join([f'''
### {measure.category}
**Priority:** {measure.implementation_priority}

**Measures:**
{chr(10).join(f'- {m}' for m in measure.measures)}

**Compliance Requirements:**
{chr(10).join(f'- {req}' for req in (measure.compliance_requirements or []))}

**Threat Mitigations:**
{json.dumps(measure.threat_mitigations, indent=2) if measure.threat_mitigations else "N/A"}
''' for measure in architecture.security_measures])}

## Deployment Strategy
{chr(10).join([f'''
### Stage: {stage.name}

**Components:**
{chr(10).join(f'- {comp}' for comp in stage.components)}

**Prerequisites:**
{chr(10).join(f'- {pre}' for pre in stage.prerequisites)}

**Success Criteria:**
{chr(10).join(f'- {crit}' for crit in stage.success_criteria)}

**Rollback Plan:**
{chr(10).join(f'- {plan}' for plan in stage.rollback_plan)}

**Monitoring Metrics:**
{chr(10).join(f'- {metric}' for metric in (stage.monitoring_metrics or []))}

**Environment Configuration:**
{json.dumps(stage.environment_config, indent=2) if stage.environment_config else "N/A"}
''' for stage in architecture.deployment_strategy])}

## Design Patterns
{chr(10).join(f'- {pattern}' for pattern in architecture.design_patterns)}

## Scalability Considerations
{chr(10).join(f'- {consideration}' for consideration in architecture.scalability_considerations)}

## Monitoring Requirements
{chr(10).join(f'- {req}' for req in architecture.monitoring_requirements)}

## API Documentation
{json.dumps(architecture.api_documentation, indent=2) if architecture.api_documentation else "N/A"}

## Performance Benchmarks
{json.dumps(architecture.performance_benchmarks, indent=2) if architecture.performance_benchmarks else "N/A"}

## Disaster Recovery Plan
{json.dumps(architecture.disaster_recovery_plan, indent=2) if architecture.disaster_recovery_plan else "N/A"}
"""

            with output_path.open('w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Architecture saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving architecture: {str(e)}")
            raise

@click.command()
@click.argument('specs_file', type=click.Path(exists=True))
@click.argument('brainstorm_file', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
async def main(specs_file: str, brainstorm_file: str, output: str):
    """Generate system architecture using the Architect agent."""
    try:
        # Read input files
        with open(specs_file, 'r') as f:
            specs = f.read()
        
        with open(brainstorm_file, 'r') as f:
            brainstorm = f.read()
        
        # Initialize architect and generate architecture
        architect = Architect()
        architecture = await architect.generate_architecture(specs, brainstorm)
        
        # Save architecture
        architect.save_architecture(architecture, output)
        
    except Exception as e:
        logger.error(f"Error in architecture generation: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
