import click
from loguru import logger
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import asyncio
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

class Task(BaseModel):
    id: str
    name: str
    description: str
    component: str
    dependencies: List[str]
    estimated_effort: str
    complexity: str
    technical_requirements: List[str]
    acceptance_criteria: List[str]
    test_requirements: Optional[List[str]] = None
    ai_integration_points: Optional[List[str]] = None

class FileStructure(BaseModel):
    path: str
    type: str  # 'directory' or 'file'
    description: str
    contents: Optional[List['FileStructure']] = None
    template: Optional[str] = None
    dependencies: Optional[List[str]] = None

class AIIntegrationPoint(BaseModel):
    component: str
    purpose: str
    model_requirements: List[str]
    input_format: Dict[str, Any]
    output_format: Dict[str, Any]
    validation_rules: List[str]
    fallback_strategy: Optional[str] = None

class DevelopmentPlan(BaseModel):
    overview: str
    tasks: List[Task]
    file_structure: List[FileStructure]
    dependencies: Dict[str, List[str]]
    ai_integration_points: List[AIIntegrationPoint]
    development_phases: List[Dict[str, Any]]
    risk_mitigation: Dict[str, List[str]]
    quality_gates: List[Dict[str, Any]]
    session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

class Planner:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Planner with Gemini configuration."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)

    async def generate_tasks(self, 
                           specs: Dict[str, Any], 
                           architecture: Dict[str, Any]) -> List[Task]:
        """Generate detailed task breakdown."""
        try:
            prompt = f"""Analyze the product specifications and system architecture to create a detailed task breakdown.

            Product Specifications:
            {json.dumps(specs, indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}

            For each component and major feature, create tasks that:
            1. Have clear dependencies and relationships
            2. Include effort estimates and complexity ratings
            3. Specify technical requirements and acceptance criteria
            4. Identify test requirements and AI integration points

            Format as JSON array of Task objects.
            """

            response = await self.client.generate_content(prompt)
            tasks_data = json.loads(response.text)
            return [Task(**task) for task in tasks_data]

        except Exception as e:
            logger.error(f"Error generating tasks: {str(e)}")
            raise

    async def generate_file_structure(self, 
                                    specs: Dict[str, Any], 
                                    architecture: Dict[str, Any]) -> List[FileStructure]:
        """Generate detailed file and directory structure."""
        try:
            prompt = f"""Design a comprehensive file structure based on the specifications and architecture.

            Product Specifications:
            {json.dumps(specs, indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}

            Create a file structure that:
            1. Follows best practices for the chosen tech stack
            2. Organizes code logically by feature/component
            3. Includes necessary configuration and documentation
            4. Provides templates for key files
            5. Specifies dependencies between files

            Format as JSON array of FileStructure objects.
            """

            response = await self.client.generate_content(prompt)
            structure_data = json.loads(response.text)
            return [FileStructure(**item) for item in structure_data]

        except Exception as e:
            logger.error(f"Error generating file structure: {str(e)}")
            raise

    async def identify_ai_integration_points(self, 
                                          tasks: List[Task], 
                                          architecture: Dict[str, Any]) -> List[AIIntegrationPoint]:
        """Identify opportunities for AI integration."""
        try:
            prompt = f"""Analyze the tasks and architecture to identify AI integration opportunities.

            Tasks:
            {json.dumps([task.dict() for task in tasks], indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}

            For each potential AI integration point, specify:
            1. Purpose and expected benefits
            2. Required model capabilities
            3. Input/output formats
            4. Validation requirements
            5. Fallback strategies

            Format as JSON array of AIIntegrationPoint objects.
            """

            response = await self.client.generate_content(prompt)
            integration_data = json.loads(response.text)
            return [AIIntegrationPoint(**point) for point in integration_data]

        except Exception as e:
            logger.error(f"Error identifying AI integration points: {str(e)}")
            raise

    async def generate_development_phases(self, 
                                       tasks: List[Task], 
                                       architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate development phases with quality gates."""
        try:
            prompt = f"""Create a phased development plan with quality gates.

            Tasks:
            {json.dumps([task.dict() for task in tasks], indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}

            For each development phase:
            1. Group related tasks
            2. Define entry/exit criteria
            3. Specify quality gates and checkpoints
            4. Identify risk factors
            5. Plan for continuous integration

            Format as JSON array of phase objects.
            """

            response = await self.client.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"Error generating development phases: {str(e)}")
            raise

    async def generate_development_plan(self, 
                                     specs: str, 
                                     architecture: str) -> DevelopmentPlan:
        """Generate comprehensive development plan."""
        try:
            # Parse input JSON
            specs_data = json.loads(specs)
            arch_data = json.loads(architecture)

            # Generate plan components in parallel
            tasks = await self.generate_tasks(specs_data, arch_data)
            file_structure = await self.generate_file_structure(specs_data, arch_data)
            ai_integration_points = await self.identify_ai_integration_points(tasks, arch_data)
            development_phases = await self.generate_development_phases(tasks, arch_data)

            # Generate risk mitigation strategies
            risk_prompt = f"""Identify potential risks and mitigation strategies for the development plan.

            Tasks:
            {json.dumps([task.dict() for task in tasks], indent=2)}

            Development Phases:
            {json.dumps(development_phases, indent=2)}

            Format as JSON object with risk categories as keys and mitigation strategies as arrays.
            """

            risk_response = await self.client.generate_content(risk_prompt)
            risk_mitigation = json.loads(risk_response.text)

            # Generate quality gates
            gates_prompt = f"""Define quality gates for the development process.

            Development Phases:
            {json.dumps(development_phases, indent=2)}

            AI Integration Points:
            {json.dumps([point.dict() for point in ai_integration_points], indent=2)}

            Format as JSON array of quality gate objects.
            """

            gates_response = await self.client.generate_content(gates_prompt)
            quality_gates = json.loads(gates_response.text)

            # Create dependencies map
            dependencies = {}
            for task in tasks:
                for dep in task.dependencies:
                    if dep not in dependencies:
                        dependencies[dep] = []
                    dependencies[dep].append(task.id)

            # Generate overview
            overview_prompt = f"""Create a concise overview of the development plan.

            Key Information:
            - Number of tasks: {len(tasks)}
            - Number of development phases: {len(development_phases)}
            - Number of AI integration points: {len(ai_integration_points)}
            - Number of quality gates: {len(quality_gates)}

            Format as a single string summarizing the plan's approach and key aspects.
            """

            overview_response = await self.client.generate_content(overview_prompt)
            overview = overview_response.text.strip()

            # Create and return complete plan
            return DevelopmentPlan(
                overview=overview,
                tasks=tasks,
                file_structure=file_structure,
                dependencies=dependencies,
                ai_integration_points=ai_integration_points,
                development_phases=development_phases,
                risk_mitigation=risk_mitigation,
                quality_gates=quality_gates
            )

        except Exception as e:
            logger.error(f"Error generating development plan: {str(e)}")
            raise

    def save_plan(self, plan: DevelopmentPlan, output_file: str):
        """Save the development plan to a markdown file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            markdown_content = f"""# Development Plan
Session ID: {plan.session_id}

## Overview
{plan.overview}

## Tasks
{chr(10).join([f'''
### {task.id}: {task.name}
{task.description}

**Component:** {task.component}
**Effort:** {task.estimated_effort}
**Complexity:** {task.complexity}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in task.dependencies)}

**Technical Requirements:**
{chr(10).join(f'- {req}' for req in task.technical_requirements)}

**Acceptance Criteria:**
{chr(10).join(f'- {crit}' for crit in task.acceptance_criteria)}

**Test Requirements:**
{chr(10).join(f'- {test}' for test in (task.test_requirements or []))}

**AI Integration Points:**
{chr(10).join(f'- {point}' for point in (task.ai_integration_points or []))}
''' for task in plan.tasks])}

## File Structure
{chr(10).join([f'''
### {item.path}
**Type:** {item.type}
{item.description}

**Template:**
{item.template if item.template else "N/A"}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in (item.dependencies or []))}

**Contents:**
{chr(10).join(f'- {content.path}' for content in (item.contents or []))}
''' for item in plan.file_structure])}

## AI Integration Points
{chr(10).join([f'''
### {point.component}
**Purpose:** {point.purpose}

**Model Requirements:**
{chr(10).join(f'- {req}' for req in point.model_requirements)}

**Input Format:**
{json.dumps(point.input_format, indent=2)}

**Output Format:**
{json.dumps(point.output_format, indent=2)}

**Validation Rules:**
{chr(10).join(f'- {rule}' for rule in point.validation_rules)}

**Fallback Strategy:**
{point.fallback_strategy if point.fallback_strategy else "N/A"}
''' for point in plan.ai_integration_points])}

## Development Phases
{chr(10).join([f'''
### Phase {i+1}: {phase['name']}
{phase['description']}

**Tasks:**
{chr(10).join(f'- {task}' for task in phase['tasks'])}

**Entry Criteria:**
{chr(10).join(f'- {crit}' for crit in phase['entry_criteria'])}

**Exit Criteria:**
{chr(10).join(f'- {crit}' for crit in phase['exit_criteria'])}

**Risk Factors:**
{chr(10).join(f'- {risk}' for risk in phase['risk_factors'])}
''' for i, phase in enumerate(plan.development_phases)])}

## Risk Mitigation
{chr(10).join([f'''
### {category}
{chr(10).join(f'- {strategy}' for strategy in strategies)}
''' for category, strategies in plan.risk_mitigation.items()])}

## Quality Gates
{chr(10).join([f'''
### {gate['name']}
{gate['description']}

**Criteria:**
{chr(10).join(f'- {crit}' for crit in gate['criteria'])}

**Verification Methods:**
{chr(10).join(f'- {method}' for method in gate['verification_methods'])}
''' for gate in plan.quality_gates])}
"""

            with output_path.open('w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Development plan saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving plan: {str(e)}")
            raise

@click.command()
@click.argument('specs_file', type=click.Path(exists=True))
@click.argument('architecture_file', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
async def main(specs_file: str, architecture_file: str, output: str):
    """Generate development plan using the Planner agent."""
    try:
        # Read input files
        with open(specs_file, 'r') as f:
            specs = f.read()
        
        with open(architecture_file, 'r') as f:
            architecture = f.read()
        
        # Initialize planner and generate plan
        planner = Planner()
        plan = await planner.generate_development_plan(specs, architecture)
        
        # Save plan
        planner.save_plan(plan, output)
        
    except Exception as e:
        logger.error(f"Error in plan generation: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
