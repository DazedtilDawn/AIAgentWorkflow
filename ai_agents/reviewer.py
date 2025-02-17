import click
import os
from loguru import logger
from typing import Dict, List, Tuple
from .base_agent import BaseAgent

class Reviewer(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
    
    async def review_code(self, 
                         code: str,
                         context: Dict) -> Tuple[List[Dict], bool]:
        """Review code for quality, style, and potential issues."""
        system_message = """You are an Expert Code Reviewer evaluating code for quality, 
        maintainability, and adherence to best practices. Be thorough but constructive 
        in your feedback."""
        
        prompt = f"""Review the following code:

        {code}

        Context:
        {context}

        Evaluate the code for:
        1. Code Quality
           - Clean code principles
           - SOLID principles
           - Design patterns
        2. Performance
           - Algorithm efficiency
           - Resource usage
           - Scalability
        3. Security
           - Potential vulnerabilities
           - Input validation
           - Authentication/Authorization
        4. Maintainability
           - Code organization
           - Documentation
           - Test coverage
        5. Error Handling
           - Edge cases
           - Error recovery
           - Logging
        """
        
        try:
            review = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_review(review)
        except Exception as e:
            logger.error(f"Error reviewing code: {str(e)}")
            raise
    
    async def analyze_test_coverage(self, 
                                  code: str,
                                  tests: str) -> Dict:
        """Analyze test coverage and identify gaps."""
        system_message = """You are a Test Coverage Analyst evaluating the completeness 
        and effectiveness of test suites."""
        
        prompt = f"""Analyze the following code and its tests:

        Code:
        {code}

        Tests:
        {tests}

        Evaluate:
        1. Test Coverage
           - Line coverage
           - Branch coverage
           - Path coverage
        2. Test Quality
           - Edge cases
           - Error conditions
           - Integration points
        3. Missing Tests
           - Untested functionality
           - Incomplete scenarios
           - Security tests
        """
        
        try:
            analysis = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_coverage_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing test coverage: {str(e)}")
            raise
    
    async def security_audit(self, code: str) -> List[Dict]:
        """Perform security audit of the code."""
        system_message = """You are a Security Auditor identifying potential security 
        vulnerabilities and recommending mitigations."""
        
        prompt = f"""Audit the following code for security issues:

        {code}

        Check for:
        1. Common Vulnerabilities
           - Injection flaws
           - Authentication issues
           - Authorization bypass
           - Data exposure
        2. Secure Coding Practices
           - Input validation
           - Output encoding
           - Secure communications
        3. Data Protection
           - Sensitive data handling
           - Encryption usage
           - Access controls
        """
        
        try:
            audit = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_security_audit(audit)
        except Exception as e:
            logger.error(f"Error performing security audit: {str(e)}")
            raise
    
    def _parse_review(self, raw_review: str) -> Tuple[List[Dict], bool]:
        """Parse the raw review into structured format and approval status."""
        # Implementation would parse the text into structured data
        return [{"content": raw_review}], True  # Simplified for example
    
    def _parse_coverage_analysis(self, raw_analysis: str) -> Dict:
        """Parse the raw coverage analysis into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_analysis}  # Simplified for example
    
    def _parse_security_audit(self, raw_audit: str) -> List[Dict]:
        """Parse the raw security audit into structured format."""
        # Implementation would parse the text into structured data
        return [{"content": raw_audit}]  # Simplified for example
    
    def _generate_review_report(self,
                              code_reviews: List[Dict],
                              coverage_analysis: Dict,
                              security_audit: List[Dict]) -> str:
        """Generate comprehensive review report."""
        report = ["# Code Review Report\n\n"]
        
        # Add code reviews
        report.append("## Code Quality Review\n")
        for review in code_reviews:
            report.append(f"- {review.get('content')}\n")
        
        # Add coverage analysis
        report.append("\n## Test Coverage Analysis\n")
        report.append(coverage_analysis.get('content', ''))
        
        # Add security audit
        report.append("\n## Security Audit\n")
        for finding in security_audit:
            report.append(f"- {finding.get('content')}\n")
        
        return "".join(report)

@click.command()
@click.option('--commit-summary', required=True, help='Path to the commit summary file')
@click.option('--code-dir', required=True, help='Directory containing the code to review')
@click.option('--output', required=True, help='Path to save the review report')
def main(commit_summary: str, code_dir: str, output: str):
    """CLI interface for the Reviewer agent."""
    try:
        reviewer = Reviewer()
        
        if not reviewer.validate_file_exists(commit_summary):
            raise FileNotFoundError(f"Commit summary not found: {commit_summary}")
        
        if not os.path.isdir(code_dir):
            raise NotADirectoryError(f"Code directory not found: {code_dir}")
        
        # Load commit summary for context
        context = reviewer.load_file(commit_summary)
        
        code_reviews = []
        coverage_analyses = {}
        security_findings = []
        
        # Review each Python file in the code directory
        for filename in os.listdir(code_dir):
            if filename.endswith('.py') and not filename.startswith('test_'):
                file_path = os.path.join(code_dir, filename)
                test_path = os.path.join(code_dir, f"test_{filename}")
                
                # Load code and tests
                code = reviewer.load_file(file_path)
                tests = reviewer.load_file(test_path) if os.path.exists(test_path) else ""
                
                # Perform reviews
                review_results, approved = reviewer.review_code(code, {"context": context})
                code_reviews.extend(review_results)
                
                coverage_analysis = reviewer.analyze_test_coverage(code, tests)
                coverage_analyses[filename] = coverage_analysis
                
                security_audit = reviewer.security_audit(code)
                security_findings.extend(security_audit)
        
        # Generate and save review report
        report = reviewer._generate_review_report(
            code_reviews,
            coverage_analyses,
            security_findings
        )
        reviewer.save_file(output, report)
        
        logger.info(f"Successfully generated review report: {output}")
        
    except Exception as e:
        logger.error(f"Error in reviewer execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
