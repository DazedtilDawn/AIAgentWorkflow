import click
import os
from loguru import logger
from typing import Dict, List, Optional
from .base_agent import BaseAgent

class Engineer(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
    
    async def generate_component_code(self, 
                                   component_spec: Dict,
                                   existing_code: Optional[str] = None) -> str:
        """Generate implementation code for a component."""
        system_message = """You are an Expert Software Engineer implementing high-quality, 
        production-ready code. Focus on clean code principles, proper error handling, 
        and comprehensive documentation."""
        
        context = f"Existing code:\n{existing_code}\n" if existing_code else ""
        prompt = f"""{context}
        Based on the following component specification:

        {component_spec}

        Generate production-ready implementation code that includes:
        1. Proper imports and dependencies
        2. Class and function implementations
        3. Error handling
        4. Input validation
        5. Logging
        6. Type hints
        7. Docstrings and comments
        8. Unit test scaffolding
        """
        
        try:
            code = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._format_code(code)
        except Exception as e:
            logger.error(f"Error generating component code: {str(e)}")
            raise
    
    async def generate_tests(self, 
                           component_code: str,
                           test_requirements: Dict) -> str:
        """Generate comprehensive tests for a component."""
        system_message = """You are a Test Engineer creating comprehensive test suites. 
        Focus on test coverage, edge cases, and maintainable test code."""
        
        prompt = f"""For the following component implementation:

        {component_code}

        And test requirements:
        {test_requirements}

        Generate a comprehensive test suite that includes:
        1. Unit tests
           - Happy path scenarios
           - Edge cases
           - Error conditions
        2. Integration tests
           - Component interactions
           - External service mocking
        3. Performance tests
           - Load testing scenarios
           - Resource usage checks
        """
        
        try:
            tests = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._format_code(tests)
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            raise
    
    async def optimize_code(self, 
                          code: str,
                          performance_requirements: Dict) -> str:
        """Optimize code based on performance requirements."""
        system_message = """You are a Performance Optimization Engineer improving code 
        efficiency while maintaining readability and maintainability."""
        
        prompt = f"""Optimize the following code:

        {code}

        Based on these performance requirements:
        {performance_requirements}

        Focus on:
        1. Algorithm efficiency
        2. Memory usage
        3. CPU utilization
        4. I/O operations
        5. Caching strategies
        6. Resource pooling
        
        Maintain:
        1. Code readability
        2. Maintainability
        3. Error handling
        4. Testing capability
        """
        
        try:
            optimized_code = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._format_code(optimized_code)
        except Exception as e:
            logger.error(f"Error optimizing code: {str(e)}")
            raise
    
    def _format_code(self, raw_code: str) -> str:
        """Format generated code according to style guidelines."""
        try:
            # Implementation would use tools like black, isort, etc.
            return raw_code  # Simplified for example
        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            raise
    
    def _generate_commit_summary(self, 
                               changes: List[Dict],
                               performance_metrics: Optional[Dict] = None) -> str:
        """Generate a detailed commit summary."""
        summary = ["# Code Implementation Summary\n"]
        
        # Add changes
        summary.append("## Changes Made\n")
        for change in changes:
            summary.append(f"- {change.get('file')}: {change.get('description')}\n")
        
        # Add performance metrics if available
        if performance_metrics:
            summary.append("\n## Performance Metrics\n")
            for metric, value in performance_metrics.items():
                summary.append(f"- {metric}: {value}\n")
        
        return "".join(summary)

@click.command()
@click.option('--plan', required=True, help='Path to the development plan file')
@click.option('--output-code', required=True, help='Directory to save generated code')
@click.option('--commit-summary', required=True, help='Path to save the commit summary')
def main(plan: str, output_code: str, commit_summary: str):
    """CLI interface for the Engineer agent."""
    try:
        engineer = Engineer()
        
        if not engineer.validate_file_exists(plan):
            raise FileNotFoundError(f"Development plan not found: {plan}")
        
        # Load development plan
        plan_content = engineer.load_file(plan)
        plan_data = eval(plan_content)  # Convert string to dict (simplified)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_code, exist_ok=True)
        
        changes = []
        performance_metrics = {}
        
        # Generate code for each component
        for component in plan_data.get("component_details", []):
            # Generate component code
            code = engineer.generate_component_code(component)
            
            # Generate tests
            tests = engineer.generate_tests(code, component.get("test_requirements", {}))
            
            # Optimize if performance requirements specified
            if "performance_requirements" in component:
                code = engineer.optimize_code(code, component["performance_requirements"])
            
            # Save component code
            component_path = os.path.join(output_code, f"{component['name']}.py")
            engineer.save_file(component_path, code)
            
            # Save component tests
            test_path = os.path.join(output_code, f"test_{component['name']}.py")
            engineer.save_file(test_path, tests)
            
            changes.append({
                "file": component_path,
                "description": f"Implemented {component['name']} component"
            })
            changes.append({
                "file": test_path,
                "description": f"Added tests for {component['name']} component"
            })
        
        # Generate and save commit summary
        summary = engineer._generate_commit_summary(changes, performance_metrics)
        engineer.save_file(commit_summary, summary)
        
        logger.info(f"Successfully generated code in: {output_code}")
        logger.info(f"Commit summary saved to: {commit_summary}")
        
    except Exception as e:
        logger.error(f"Error in engineer execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
