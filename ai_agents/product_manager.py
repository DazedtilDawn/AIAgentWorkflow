import click
from loguru import logger
from typing import Optional
from .base_agent import BaseAgent

class ProductManager(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
        
    async def generate_product_specs(self, project_context: Optional[str] = None) -> str:
        """Generate product specifications based on project context."""
        system_message = """You are an experienced Product Manager tasked with creating detailed 
        product specifications. Focus on user needs, technical requirements, success metrics, 
        and clear deliverables. Be specific and actionable."""
        
        prompt = f"""Create a detailed product specification document that includes:
        1. Product Overview
        2. Target Audience
        3. User Stories
        4. Technical Requirements
        5. Success Metrics
        6. Deliverables Timeline
        7. Risk Assessment

        Additional Context:
        {project_context if project_context else 'No additional context provided.'}
        """
        
        try:
            specs = await self.get_completion(prompt, system_message, temperature=0.7)
            return specs
        except Exception as e:
            logger.error(f"Error generating product specs: {str(e)}")
            raise

@click.command()
@click.option('--output', required=True, help='Path to save the product specifications')
@click.option('--context-file', help='Optional path to a file containing project context')
def main(output: str, context_file: Optional[str] = None):
    """CLI interface for the Product Manager agent."""
    try:
        pm = ProductManager()
        context = None
        if context_file:
            if pm.validate_file_exists(context_file):
                context = pm.load_file(context_file)
        
        specs = pm.generate_product_specs(context)
        pm.save_file(output, specs)
        logger.info(f"Successfully generated product specifications: {output}")
        
    except Exception as e:
        logger.error(f"Error in product manager execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
