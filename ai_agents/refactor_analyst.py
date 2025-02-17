import click
import os
from loguru import logger
from typing import Dict, List, Optional
from .base_agent import BaseAgent

class RefactorAnalyst(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
    
    async def analyze_code_quality(self, 
                                 code: str,
                                 metrics: Optional[Dict] = None) -> Dict:
        """Analyze code quality and identify refactoring opportunities."""
        system_message = """You are a Code Quality Analyst specializing in identifying 
        refactoring opportunities and architectural improvements. Focus on maintainability, 
        performance, and modern best practices."""
        
        context = f"Performance metrics:\n{metrics}\n" if metrics else ""
        prompt = f"""{context}
        Analyze the following code:

        {code}

        Identify opportunities for improvement in:
        1. Code Structure
           - Design patterns
           - SOLID principles
           - Component organization
        2. Performance
           - Algorithm efficiency
           - Resource usage
           - Caching strategies
        3. Maintainability
           - Code duplication
           - Complexity
           - Documentation
        4. Modern Practices
           - Latest language features
           - Framework capabilities
           - Industry standards
        """
        
        try:
            analysis = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing code quality: {str(e)}")
            raise
    
    async def generate_refactor_suggestions(self, 
                                          analysis: Dict,
                                          constraints: Optional[Dict] = None) -> List[Dict]:
        """Generate specific refactoring suggestions."""
        system_message = """You are a Refactoring Expert providing actionable 
        suggestions for code improvements. Focus on practical, high-impact changes."""
        
        context = f"Project constraints:\n{constraints}\n" if constraints else ""
        prompt = f"""{context}
        Based on the following analysis:

        {analysis}

        Generate specific refactoring suggestions that:
        1. Are practical and actionable
        2. Provide clear implementation steps
        3. Include effort estimation
        4. Consider risk factors
        5. Prioritize based on impact
        
        For each suggestion, provide:
        1. Description of the change
        2. Implementation approach
        3. Expected benefits
        4. Potential risks
        5. Testing requirements
        """
        
        try:
            suggestions = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_suggestions(suggestions)
        except Exception as e:
            logger.error(f"Error generating refactor suggestions: {str(e)}")
            raise
    
    async def update_cursor_rules(self, 
                                suggestions: List[Dict],
                                existing_rules: Optional[str] = None) -> str:
        """Update .cursorrules based on refactoring insights."""
        system_message = """You are a Development Tools Expert updating IDE rules 
        to enforce best practices and maintain code quality."""
        
        context = f"Existing rules:\n{existing_rules}\n" if existing_rules else ""
        prompt = f"""{context}
        Based on the following refactoring suggestions:

        {suggestions}

        Generate updated .cursorrules that:
        1. Enforce best practices
        2. Prevent common issues
        3. Maintain consistency
        4. Support modern patterns
        
        Include rules for:
        1. Code style
        2. Pattern usage
        3. Performance practices
        4. Security guidelines
        5. Testing requirements
        """
        
        try:
            rules = await self.get_completion(prompt, system_message, temperature=0.5)
            return self._format_cursor_rules(rules)
        except Exception as e:
            logger.error(f"Error updating cursor rules: {str(e)}")
            raise
    
    def _parse_analysis(self, raw_analysis: str) -> Dict:
        """Parse the raw analysis into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_analysis}  # Simplified for example
    
    def _parse_suggestions(self, raw_suggestions: str) -> List[Dict]:
        """Parse the raw suggestions into structured format."""
        # Implementation would parse the text into structured data
        return [{"content": raw_suggestions}]  # Simplified for example
    
    def _format_cursor_rules(self, raw_rules: str) -> str:
        """Format the raw rules into .cursorrules format."""
        # Implementation would format the rules appropriately
        return raw_rules  # Simplified for example
    
    def _generate_refactor_report(self,
                                analysis: Dict,
                                suggestions: List[Dict],
                                rules_update: str) -> str:
        """Generate comprehensive refactoring report."""
        report = ["# Code Refactoring Analysis\n\n"]
        
        # Add code quality analysis
        report.append("## Code Quality Analysis\n")
        report.append(analysis.get('content', ''))
        
        # Add refactoring suggestions
        report.append("\n## Refactoring Suggestions\n")
        for suggestion in suggestions:
            report.append(f"### {suggestion.get('title', 'Suggestion')}\n")
            report.append(suggestion.get('content', ''))
            report.append("\n")
        
        # Add cursor rules update
        report.append("\n## Updated Cursor Rules\n")
        report.append("```\n")
        report.append(rules_update)
        report.append("\n```\n")
        
        return "".join(report)

@click.command()
@click.option('--code-dir', required=True, help='Directory containing the code to analyze')
@click.option('--metrics-file', help='Optional path to performance metrics file')
@click.option('--constraints-file', help='Optional path to project constraints file')
@click.option('--cursor-rules', help='Optional path to existing .cursorrules file')
@click.option('--output', required=True, help='Path to save the refactoring report')
def main(code_dir: str,
         metrics_file: Optional[str],
         constraints_file: Optional[str],
         cursor_rules: Optional[str],
         output: str):
    """CLI interface for the Refactor Analyst."""
    try:
        analyst = RefactorAnalyst()
        
        if not os.path.isdir(code_dir):
            raise NotADirectoryError(f"Code directory not found: {code_dir}")
        
        # Load optional files
        metrics = None
        if metrics_file and analyst.validate_file_exists(metrics_file):
            metrics = json.loads(analyst.load_file(metrics_file))
        
        constraints = None
        if constraints_file and analyst.validate_file_exists(constraints_file):
            constraints = json.loads(analyst.load_file(constraints_file))
        
        existing_rules = None
        if cursor_rules and analyst.validate_file_exists(cursor_rules):
            existing_rules = analyst.load_file(cursor_rules)
        
        # Analyze all Python files in the directory
        all_code = ""
        for root, _, files in os.walk(code_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    all_code += f"\n# File: {file}\n"
                    all_code += analyst.load_file(file_path)
        
        # Perform analysis
        analysis = analyst.analyze_code_quality(all_code, metrics)
        suggestions = analyst.generate_refactor_suggestions(analysis, constraints)
        rules_update = analyst.update_cursor_rules(suggestions, existing_rules)
        
        # Generate and save report
        report = analyst._generate_refactor_report(
            analysis,
            suggestions,
            rules_update
        )
        analyst.save_file(output, report)
        
        # Save updated cursor rules if path provided
        if cursor_rules:
            analyst.save_file(cursor_rules, rules_update)
        
        logger.info(f"Successfully generated refactoring report: {output}")
        if cursor_rules:
            logger.info(f"Updated cursor rules: {cursor_rules}")
        
    except Exception as e:
        logger.error(f"Error in refactor analyst execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
