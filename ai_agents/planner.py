import click
from loguru import logger
from typing import Dict, List
from .base_agent import BaseAgent

class Planner(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
    
    async def generate_development_plan(self, architecture: str) -> Dict:
        """Generate detailed development plan based on system architecture."""
        system_message = """You are a Technical Project Planner responsible for creating 
        detailed development plans. Break down the architecture into actionable tasks, 
        considering dependencies, complexity, and resource requirements."""
        
        prompt = f"""Based on the following system architecture:

        {architecture}

        Create a detailed development plan that includes:
        1. Task Breakdown
           - Components to be developed
           - Dependencies between components
           - Estimated complexity and effort
        2. File Structure
           - Directory organization
           - Key files and their purposes
        3. Implementation Order
           - Critical path identification
           - Parallel development opportunities
        4. Testing Strategy
           - Unit test requirements
           - Integration test points
           - End-to-end test scenarios
        5. Documentation Requirements
           - API documentation
           - Development guides
           - Deployment instructions
        """
        
        try:
            plan = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_plan(plan)
        except Exception as e:
            logger.error(f"Error generating development plan: {str(e)}")
            raise
    
    async def generate_pseudocode(self, component_specs: Dict) -> str:
        """Generate pseudocode for specific components."""
        system_message = """You are a Technical Designer creating detailed pseudocode 
        for software components. Focus on clarity, maintainability, and best practices."""
        
        prompt = f"""For the following component specifications:

        {component_specs}

        Generate detailed pseudocode that includes:
        1. Function signatures
        2. Class structures
        3. Data models
        4. Key algorithms
        5. Error handling
        6. Comments explaining complex logic
        """
        
        try:
            pseudocode = await self.get_completion(prompt, system_message, temperature=0.6)
            return pseudocode
        except Exception as e:
            logger.error(f"Error generating pseudocode: {str(e)}")
            raise
    
    async def identify_external_integrations(self, plan: Dict) -> List[Dict]:
        """Identify required external integrations and their specifications."""
        system_message = """You are a Systems Integration Specialist identifying and 
        specifying external service integrations needed for the project."""
        
        prompt = f"""Based on the development plan:

        {plan}

        Identify all required external integrations:
        1. Third-party services
        2. APIs
        3. Libraries and frameworks
        4. Infrastructure services
        
        For each integration, specify:
        1. Purpose and functionality
        2. Authentication requirements
        3. Rate limits and quotas
        4. Cost implications
        5. Implementation considerations
        """
        
        try:
            integrations = await self.get_completion(prompt, system_message, temperature=0.5)
            return self._parse_integrations(integrations)
        except Exception as e:
            logger.error(f"Error identifying integrations: {str(e)}")
            raise
    
    def _parse_plan(self, raw_plan: str) -> Dict:
        """Parse the raw development plan into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_plan}  # Simplified for example
    
    def _parse_integrations(self, raw_integrations: str) -> List[Dict]:
        """Parse the raw integrations into structured format."""
        # Implementation would parse the text into structured data
        return [{"content": raw_integrations}]  # Simplified for example

@click.command()
@click.option('--architecture-file', required=True, help='Path to the system architecture file')
@click.option('--output', required=True, help='Path to save the development plan')
def main(architecture_file: str, output: str):
    """CLI interface for the Planner agent."""
    try:
        planner = Planner()
        
        if not planner.validate_file_exists(architecture_file):
            raise FileNotFoundError(f"Architecture file not found: {architecture_file}")
        
        architecture = planner.load_file(architecture_file)
        plan = planner.generate_development_plan(architecture)
        
        # Generate additional planning artifacts
        components = plan.get("components", [])
        for component in components:
            component["pseudocode"] = planner.generate_pseudocode(component)
        
        integrations = planner.identify_external_integrations(plan)
        
        # Combine all planning artifacts
        final_plan = {
            "development_plan": plan,
            "component_details": components,
            "external_integrations": integrations
        }
        
        planner.save_file(output, str(final_plan))
        logger.info(f"Successfully generated development plan: {output}")
        
    except Exception as e:
        logger.error(f"Error in planner execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
