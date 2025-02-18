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

    async def generate_tasks(self, 
                           specs: Dict[str, Any], 
                           architecture: Dict[str, Any]) -> List[Task]:
        """Generate detailed task breakdown."""
        try:
            prompt = f"""Design a comprehensive task breakdown based on the specifications and architecture.
            Return the response in JSON format as an array of tasks.
            Each task should have the following structure:
            {{
                "id": "unique_id",
                "name": "task name",
                "description": "detailed description",
                "component": "component name",
                "dependencies": ["dep1", "dep2"],
                "estimated_effort": "effort estimate",
                "complexity": "high/medium/low",
                "technical_requirements": ["req1", "req2"],
                "acceptance_criteria": ["criteria1", "criteria2"],
                "test_requirements": ["test1", "test2"],
                "ai_integration_points": ["point1", "point2"]
            }}

            Product Specifications:
            {json.dumps(specs, indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}
            """

            logger.info("Sending prompt to Gemini model...")
            logger.debug(f"Prompt: {prompt}")
            
            # Create model for each request to ensure clean state
            model = genai.GenerativeModel(self.model)
            
            # Generate with safety settings
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info("Configuring generation parameters...")
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            logger.info("Received response from Gemini")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            
            if not response.text:
                raise ValueError("Empty response received from Gemini")
                
            logger.info("Processing response text...")
            logger.debug(f"Raw response text: {response.text}")
            
            # Clean and format the response
            response_text = response.text.strip()
            if response_text.startswith('```') and response_text.endswith('```'):
                response_text = response_text[3:-3].strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
                
            logger.debug(f"Cleaned response text: {response_text}")
            
            try:
                tasks_data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON with {len(tasks_data)} tasks")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Failed text: {response_text}")
                raise
            
            tasks = [Task(**task) for task in tasks_data]
            logger.info(f"Successfully created {len(tasks)} Task objects")
            return tasks

        except Exception as e:
            logger.error(f"Error in generate_tasks: {str(e)}")
            if 'response' in locals():
                logger.error(f"Response text: {response.text if response.text else 'Empty response'}")
            raise

    async def generate_file_structure(self, 
                                    specs: Dict[str, Any], 
                                    architecture: Dict[str, Any]) -> List[FileStructure]:
        """Generate file structure based on specs and architecture."""
        try:
            prompt = f"""Generate a file structure for the project based on the specifications and architecture.
            Return the response in JSON format as an array of file structures.
            Each file structure must have exactly this structure:
            {{
                "path": "relative/path/to/file",
                "type": "file",  # Must be either "file" or "directory"
                "content": "file content if type is file",  # Optional, only for files
                "description": "description of the file or directory"
            }}

            Project Specifications:
            {json.dumps(specs, indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}
            """

            logger.info("Sending prompt to Gemini model...")
            logger.debug(f"Prompt: {prompt}")
            
            # Create model for each request to ensure clean state
            model = genai.GenerativeModel(self.model)
            
            # Generate with safety settings
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info("Configuring generation parameters...")
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            logger.info("Received response from Gemini")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            
            if not response.text:
                raise ValueError("Empty response received from Gemini")
                
            logger.info("Processing response text...")
            logger.debug(f"Raw response text: {response.text}")
            
            # Clean and format the response
            response_text = response.text.strip()
            if response_text.startswith('```') and response_text.endswith('```'):
                response_text = response_text[3:-3].strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
                
            logger.debug(f"Cleaned response text: {response_text}")
            
            try:
                structure_data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON with {len(structure_data)} file structures")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Failed text: {response_text}")
                raise
            
            structure = [FileStructure(**item) for item in structure_data]
            logger.info(f"Successfully created {len(structure)} FileStructure objects")
            return structure

        except Exception as e:
            logger.error(f"Error in generate_file_structure: {str(e)}")
            logger.error(f"Response text: {response.text}")
            raise

    async def identify_ai_integration_points(self, 
                                          tasks: List[Task], 
                                          architecture: Dict[str, Any]) -> List[AIIntegrationPoint]:
        """Identify opportunities for AI integration."""
        try:
            prompt = f"""Analyze the tasks and architecture to identify AI integration opportunities.
            Return the response in JSON format as an array of AI integration points.
            Each integration point must have exactly this structure:
            {{
                "component": "component_name",
                "purpose": "detailed purpose description",
                "model_requirements": ["requirement1", "requirement2"],
                "input_format": {{"field1": "type1", "field2": "type2"}},
                "output_format": {{"field1": "type1", "field2": "type2"}},
                "validation_rules": ["rule1", "rule2"],
                "fallback_strategy": "fallback description"
            }}

            Tasks:
            {json.dumps([task.dict() for task in tasks], indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}
            """

            logger.info("Sending prompt to Gemini model...")
            logger.debug(f"Prompt: {prompt}")
            
            # Create model for each request to ensure clean state
            model = genai.GenerativeModel(self.model)
            
            # Generate with safety settings
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info("Configuring generation parameters...")
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            logger.info("Received response from Gemini")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            
            if not response.text:
                raise ValueError("Empty response received from Gemini")
                
            logger.info("Processing response text...")
            logger.debug(f"Raw response text: {response.text}")
            
            # Clean and format the response
            response_text = response.text.strip()
            if response_text.startswith('```') and response_text.endswith('```'):
                response_text = response_text[3:-3].strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
                
            logger.debug(f"Cleaned response text: {response_text}")
            
            try:
                integration_data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON with {len(integration_data)} AI integration points")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Failed text: {response_text}")
                raise
            
            integration_points = [AIIntegrationPoint(**point) for point in integration_data]
            logger.info(f"Successfully created {len(integration_points)} AIIntegrationPoint objects")
            return integration_points

        except Exception as e:
            logger.error(f"Error in identify_ai_integration_points: {str(e)}")
            if 'response' in locals():
                logger.error(f"Response text: {response.text if response.text else 'Empty response'}")
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

            logger.info("Sending prompt to Gemini model...")
            logger.debug(f"Prompt: {prompt}")
            
            # Create model for each request to ensure clean state
            model = genai.GenerativeModel(self.model)
            
            # Generate with safety settings
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info("Configuring generation parameters...")
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            logger.info("Received response from Gemini")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            
            if not response.text:
                raise ValueError("Empty response received from Gemini")
                
            logger.info("Processing response text...")
            logger.debug(f"Raw response text: {response.text}")
            
            # Clean and format the response
            response_text = response.text.strip()
            if response_text.startswith('```') and response_text.endswith('```'):
                response_text = response_text[3:-3].strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
                
            logger.debug(f"Cleaned response text: {response_text}")
            
            try:
                phases_data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON with {len(phases_data)} development phases")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Failed text: {response_text}")
                raise
            
            phases = phases_data
            logger.info(f"Successfully created {len(phases)} development phases")
            return phases

        except Exception as e:
            logger.error(f"Error in generate_development_phases: {str(e)}")
            if 'response' in locals():
                logger.error(f"Response text: {response.text if response.text else 'Empty response'}")
            raise

    async def generate_development_plan(self, specs: str, architecture: str) -> Dict[str, Any]:
        """Generate comprehensive development plan."""
        try:
            # Parse input JSON
            specs_data = json.loads(specs)
            arch_data = json.loads(architecture)
            
            logger.info("Generating tasks...")
            tasks = await self.generate_tasks(specs_data, arch_data)
            
            logger.info("Generating file structure...")
            file_structure = await self.generate_file_structure(specs_data, arch_data)
            
            logger.info("Identifying AI integration points...")
            ai_points = await self.identify_ai_integration_points(tasks, arch_data)
            
            logger.info("Generating development phases...")
            phases = await self.generate_development_phases(tasks, arch_data)
            
            # Create the plan
            plan = {
                "tasks": [task.dict() for task in tasks],
                "file_structure": [fs.dict() for fs in file_structure],
                "ai_integration_points": [point.dict() for point in ai_points],
                "development_phases": phases,
                "dependencies": {},  # Will be populated based on task relationships
                "timeline": []  # Will be generated from phases
            }
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input: {str(e)}")
            logger.error(f"Specs: {specs}")
            logger.error(f"Architecture: {architecture}")
            raise
        except Exception as e:
            logger.error(f"Error generating development plan: {str(e)}")
            raise

    def save_plan(self, plan: Dict[str, Any], output_file: str):
        """Save the development plan to a markdown file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            markdown_content = f"""# Development Plan
Session ID: {datetime.now().strftime("%Y%m%d_%H%M%S")}

## Overview
To be generated.

## Tasks
{chr(10).join([f'''
### {task['id']}: {task['name']}
{task['description']}

**Component:** {task['component']}
**Effort:** {task['estimated_effort']}
**Complexity:** {task['complexity']}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in task['dependencies'])}

**Technical Requirements:**
{chr(10).join(f'- {req}' for req in task['technical_requirements'])}

**Acceptance Criteria:**
{chr(10).join(f'- {crit}' for crit in task['acceptance_criteria'])}

**Test Requirements:**
{chr(10).join(f'- {test}' for test in (task.get('test_requirements', [])))}

**AI Integration Points:**
{chr(10).join(f'- {point}' for point in (task.get('ai_integration_points', [])))}
''' for task in plan['tasks']])}

## File Structure
{chr(10).join([f'''
### {item['path']}
**Type:** {item['type']}
{item['description']}

**Template:**
{item.get('template', "N/A")}

**Dependencies:**
{chr(10).join(f'- {dep}' for dep in (item.get('dependencies', [])))}

**Contents:**
{chr(10).join(f'- {content["path"]}' for content in (item.get('contents', [])))}
''' for item in plan['file_structure']])}

## AI Integration Points
{chr(10).join([f'''
### {point['component']}
**Purpose:** {point['purpose']}

**Model Requirements:**
{chr(10).join(f'- {req}' for req in point['model_requirements'])}

**Input Format:**
{json.dumps(point['input_format'], indent=2)}

**Output Format:**
{json.dumps(point['output_format'], indent=2)}

**Validation Rules:**
{chr(10).join(f'- {rule}' for rule in point['validation_rules'])}

**Fallback Strategy:**
{point.get('fallback_strategy', "N/A")}
''' for point in plan['ai_integration_points']])}

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
''' for i, phase in enumerate(plan['development_phases'])])}

## Risk Mitigation
To be generated.

## Quality Gates
To be generated.
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
