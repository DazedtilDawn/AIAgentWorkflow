import click
from loguru import logger
from typing import Dict, List
from .base_agent import BaseAgent

class Architect(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
    
    async def generate_architecture(self, brainstorm_outcome: str) -> Dict:
        """Generate system architecture based on brainstorm outcome."""
        system_message = """You are a seasoned Software Architect tasked with designing 
        a robust, scalable, and maintainable system architecture. Focus on modern best 
        practices, security, and scalability."""
        
        prompt = f"""Based on the following brainstorm outcome:

        {brainstorm_outcome}

        Create a detailed system architecture document that includes:
        1. System Overview
        2. Component Diagram
        3. Data Flow Architecture
        4. API Design
        5. Database Schema
        6. Security Considerations
        7. Scalability Strategy
        8. Monitoring & Logging
        9. Deployment Architecture
        10. Technology Stack Details
        """
        
        try:
            architecture = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_architecture(architecture)
        except Exception as e:
            logger.error(f"Error generating architecture: {str(e)}")
            raise
    
    async def validate_architecture(self, architecture: Dict) -> List[Dict]:
        """Validate the generated architecture against best practices."""
        system_message = """You are an Architecture Reviewer tasked with validating 
        system architecture against industry best practices and potential issues."""
        
        prompt = f"""Review the following system architecture:

        {architecture}

        Validate against:
        1. SOLID Principles
        2. Security Best Practices
        3. Scalability Requirements
        4. Maintainability
        5. Performance Considerations
        6. Cost Efficiency
        7. Technical Debt Potential
        
        Provide specific recommendations for any identified issues.
        """
        
        try:
            validation = await self.get_completion(prompt, system_message, temperature=0.4)
            return self._parse_validation(validation)
        except Exception as e:
            logger.error(f"Error validating architecture: {str(e)}")
            raise
    
    def _parse_architecture(self, raw_architecture: str) -> Dict:
        """Parse the raw architecture into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_architecture}  # Simplified for example
    
    def _parse_validation(self, raw_validation: str) -> List[Dict]:
        """Parse the raw validation into structured format."""
        # Implementation would parse the text into structured data
        return [{"content": raw_validation}]  # Simplified for example

@click.command()
@click.option('--input', required=True, help='Path to the brainstorm outcome file')
@click.option('--output', required=True, help='Path to save the system architecture')
def main(input: str, output: str):
    """CLI interface for the Architect agent."""
    try:
        architect = Architect()
        
        if not architect.validate_file_exists(input):
            raise FileNotFoundError(f"Brainstorm outcome file not found: {input}")
        
        outcome = architect.load_file(input)
        architecture = architect.generate_architecture(outcome)
        validation = architect.validate_architecture(architecture)
        
        # Combine architecture and validation into final document
        final_document = {
            "architecture": architecture,
            "validation": validation,
            "recommendations": [v.get("recommendation") for v in validation if "recommendation" in v]
        }
        
        architect.save_file(output, str(final_document))
        logger.info(f"Successfully generated system architecture: {output}")
        
    except Exception as e:
        logger.error(f"Error in architect execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
