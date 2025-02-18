import click
import os
import json
import re
from loguru import logger
from typing import Dict, List, Optional, Any
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
    
    async def analyze_dependencies(self,
                                 code_files: Dict[str, str],
                                 architecture: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze dependencies between components and identify optimization opportunities."""
        system_message = """You are a Dependency Analysis Expert focusing on component relationships,
        coupling patterns, and architectural dependencies."""
        
        files_content = "\n".join(f"File: {path}\n{content}\n" 
                                 for path, content in code_files.items())
        arch_context = f"Architecture:\n{architecture}\n" if architecture else ""
        
        prompt = f"""{arch_context}
        Analyze dependencies in the following codebase:

        {files_content}

        Focus on:
        1. Component Coupling
           - Identify tight coupling
           - Suggest decoupling strategies
           - Recommend interface improvements
        2. Dependency Patterns
           - Circular dependencies
           - Dependency injection opportunities
           - Service locator patterns
        3. Architectural Alignment
           - Layer violations
           - Boundary crossings
           - Integration patterns
        4. Optimization Opportunities
           - Shared dependencies
           - Duplicate functionality
           - Dependency consolidation
        """
        
        try:
            analysis = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_dependency_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            raise

    async def assess_refactor_impact(self,
                                   suggestions: List[Dict],
                                   codebase_stats: Dict[str, Any]) -> List[Dict]:
        """Assess the impact and risk of proposed refactoring changes."""
        system_message = """You are a Refactoring Impact Analyst specializing in
        evaluating the effects of code changes on system stability and performance."""
        
        prompt = f"""
        Analyze the impact of proposed refactoring:

        Suggestions:
        {json.dumps(suggestions, indent=2)}

        Codebase Statistics:
        {json.dumps(codebase_stats, indent=2)}

        For each suggestion, evaluate:
        1. Scope of Impact
           - Affected components
           - Downstream dependencies
           - Test coverage needs
        2. Risk Assessment
           - Technical complexity
           - Migration challenges
           - Potential regressions
        3. Resource Requirements
           - Development effort
           - Testing effort
           - Deployment complexity
        4. Business Impact
           - Performance gains
           - Maintenance benefits
           - Technical debt reduction
        """
        
        try:
            assessment = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_impact_assessment(assessment)
        except Exception as e:
            logger.error(f"Error assessing refactor impact: {str(e)}")
            raise

    async def generate_automated_refactorings(self,
                                            code: str,
                                            analysis: Dict[str, Any]) -> List[Dict]:
        """Generate automated refactoring suggestions with code examples."""
        system_message = """You are an Automated Refactoring Expert generating
        specific code changes to improve system quality."""
        
        prompt = f"""
        Generate automated refactoring suggestions for:

        Code:
        {code}

        Analysis:
        {json.dumps(analysis, indent=2)}

        For each suggestion:
        1. Provide specific code changes
        2. Include before/after examples
        3. Explain the transformation
        4. List required test updates
        5. Specify validation steps

        Focus on:
        1. Design Pattern Application
        2. SOLID Principle Alignment
        3. Performance Optimization
        4. Error Handling
        5. Resource Management
        """
        
        try:
            suggestions = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_automated_suggestions(suggestions)
        except Exception as e:
            logger.error(f"Error generating automated refactorings: {str(e)}")
            raise

    async def analyze_code(self, implementation: str, monitoring: str) -> str:
        """Wrapper method for integration test compatibility."""
        try:
            # Generate refactoring suggestions
            suggestions = await self.analyze_codebase({
                'implementation': implementation,
                'monitoring_data': monitoring
            })
            return suggestions.to_markdown()
            
        except Exception as e:
            logger.error(f"Error in analyze_code: {str(e)}")
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
    
    def _parse_dependency_analysis(self, raw_analysis: str) -> Dict[str, Any]:
        """Parse dependency analysis into structured format."""
        try:
            # Extract sections using regex
            sections = {
                "coupling": re.findall(r"Component Coupling:\n(.*?)(?=\n\n|$)", 
                                     raw_analysis, re.DOTALL),
                "patterns": re.findall(r"Dependency Patterns:\n(.*?)(?=\n\n|$)", 
                                     raw_analysis, re.DOTALL),
                "architecture": re.findall(r"Architectural Alignment:\n(.*?)(?=\n\n|$)", 
                                         raw_analysis, re.DOTALL),
                "optimization": re.findall(r"Optimization Opportunities:\n(.*?)(?=\n\n|$)", 
                                         raw_analysis, re.DOTALL)
            }
            
            # Structure the analysis
            return {
                "component_coupling": {
                    "issues": self._extract_items(sections["coupling"], r"- (.*?)(?=\n|$)"),
                    "recommendations": self._extract_items(sections["coupling"], 
                                                        r"Recommendation: (.*?)(?=\n|$)")
                },
                "dependency_patterns": {
                    "identified_patterns": self._extract_items(sections["patterns"], 
                                                            r"- (.*?)(?=\n|$)"),
                    "improvements": self._extract_items(sections["patterns"], 
                                                     r"Improvement: (.*?)(?=\n|$)")
                },
                "architectural_alignment": {
                    "violations": self._extract_items(sections["architecture"], 
                                                   r"- (.*?)(?=\n|$)"),
                    "solutions": self._extract_items(sections["architecture"], 
                                                  r"Solution: (.*?)(?=\n|$)")
                },
                "optimization_opportunities": {
                    "areas": self._extract_items(sections["optimization"], 
                                              r"- (.*?)(?=\n|$)"),
                    "suggestions": self._extract_items(sections["optimization"], 
                                                    r"Suggestion: (.*?)(?=\n|$)")
                }
            }
        except Exception as e:
            logger.error(f"Error parsing dependency analysis: {str(e)}")
            raise

    def _parse_impact_assessment(self, raw_assessment: str) -> List[Dict]:
        """Parse impact assessment into structured format."""
        try:
            # Extract individual assessments
            assessments = re.split(r"\n(?=Suggestion \d+:)", raw_assessment)
            
            parsed = []
            for assessment in assessments:
                if not assessment.strip():
                    continue
                    
                # Extract sections
                scope = re.search(r"Scope of Impact:(.*?)(?=\n\n|$)", 
                                assessment, re.DOTALL)
                risk = re.search(r"Risk Assessment:(.*?)(?=\n\n|$)", 
                               assessment, re.DOTALL)
                resources = re.search(r"Resource Requirements:(.*?)(?=\n\n|$)", 
                                    assessment, re.DOTALL)
                impact = re.search(r"Business Impact:(.*?)(?=\n\n|$)", 
                                 assessment, re.DOTALL)
                
                parsed.append({
                    "scope": {
                        "affected_components": self._extract_items(scope.group(1), 
                                                               r"- (.*?)(?=\n|$)"),
                        "dependencies": self._extract_items(scope.group(1), 
                                                        r"Dependencies: (.*?)(?=\n|$)"),
                        "test_coverage": self._extract_items(scope.group(1), 
                                                         r"Testing: (.*?)(?=\n|$)")
                    } if scope else {},
                    "risk": {
                        "complexity": self._extract_items(risk.group(1), 
                                                      r"Complexity: (.*?)(?=\n|$)"),
                        "challenges": self._extract_items(risk.group(1), 
                                                      r"Challenges: (.*?)(?=\n|$)"),
                        "regressions": self._extract_items(risk.group(1), 
                                                       r"Regressions: (.*?)(?=\n|$)")
                    } if risk else {},
                    "resources": {
                        "development": self._extract_items(resources.group(1), 
                                                       r"Development: (.*?)(?=\n|$)"),
                        "testing": self._extract_items(resources.group(1), 
                                                   r"Testing: (.*?)(?=\n|$)"),
                        "deployment": self._extract_items(resources.group(1), 
                                                      r"Deployment: (.*?)(?=\n|$)")
                    } if resources else {},
                    "business_impact": {
                        "performance": self._extract_items(impact.group(1), 
                                                       r"Performance: (.*?)(?=\n|$)"),
                        "maintenance": self._extract_items(impact.group(1), 
                                                       r"Maintenance: (.*?)(?=\n|$)"),
                        "tech_debt": self._extract_items(impact.group(1), 
                                                     r"Tech Debt: (.*?)(?=\n|$)")
                    } if impact else {}
                })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing impact assessment: {str(e)}")
            raise

    def _parse_automated_suggestions(self, raw_suggestions: str) -> List[Dict]:
        """Parse automated refactoring suggestions into structured format."""
        try:
            # Extract individual suggestions
            suggestions = re.split(r"\n(?=Suggestion \d+:)", raw_suggestions)
            
            parsed = []
            for suggestion in suggestions:
                if not suggestion.strip():
                    continue
                    
                # Extract sections
                changes = re.search(r"Code Changes:(.*?)(?=\n\n|$)", 
                                  suggestion, re.DOTALL)
                examples = re.search(r"Examples:(.*?)(?=\n\n|$)", 
                                   suggestion, re.DOTALL)
                explanation = re.search(r"Explanation:(.*?)(?=\n\n|$)", 
                                      suggestion, re.DOTALL)
                testing = re.search(r"Testing:(.*?)(?=\n\n|$)", 
                                  suggestion, re.DOTALL)
                
                parsed.append({
                    "changes": self._extract_code_changes(changes.group(1)) if changes else [],
                    "examples": {
                        "before": self._extract_code_block(examples.group(1), "Before:"),
                        "after": self._extract_code_block(examples.group(1), "After:")
                    } if examples else {},
                    "explanation": explanation.group(1).strip() if explanation else "",
                    "testing": {
                        "updates": self._extract_items(testing.group(1), 
                                                   r"- (.*?)(?=\n|$)"),
                        "validation": self._extract_items(testing.group(1), 
                                                      r"Validation: (.*?)(?=\n|$)")
                    } if testing else {}
                })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing automated suggestions: {str(e)}")
            raise

    def _extract_items(self, text: str, pattern: str) -> List[str]:
        """Extract items matching a pattern from text."""
        if not text:
            return []
        items = re.findall(pattern, text)
        return [item.strip() for item in items if item.strip()]

    def _extract_code_block(self, text: str, marker: str) -> str:
        """Extract a code block following a marker."""
        if not text:
            return ""
        match = re.search(f"{marker}\n```.*?\n(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_code_changes(self, text: str) -> List[Dict[str, str]]:
        """Extract structured code changes from text."""
        if not text:
            return []
        
        changes = []
        current_change = {}
        
        lines = text.strip().split("\n")
        for line in lines:
            if line.startswith("File:"):
                if current_change:
                    changes.append(current_change)
                current_change = {"file": line[5:].strip()}
            elif line.startswith("Line:"):
                current_change["line"] = line[5:].strip()
            elif line.startswith("Change:"):
                current_change["change"] = line[7:].strip()
        
        if current_change:
            changes.append(current_change)
            
        return changes

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
