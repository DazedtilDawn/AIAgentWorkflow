import click
import os
import json
from loguru import logger
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import json
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from loguru import logger
import ast
import re
from dataclasses import dataclass
import math

class SecurityIssue(BaseModel):
    severity: str
    category: str
    description: str
    location: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

class PerformanceMetric(BaseModel):
    category: str
    value: float
    unit: str
    threshold: float
    status: str
    recommendation: Optional[str] = None

class CodeStyle(BaseModel):
    category: str
    rule: str
    violation: str
    location: str
    suggestion: str
    severity: str

class ReviewFinding(BaseModel):
    type: str
    severity: str
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    suggestion: str
    category: str
    references: Optional[List[str]] = None

class ReviewSummary(BaseModel):
    timestamp: datetime
    commit_id: Optional[str]
    files_reviewed: List[str]
    total_findings: int
    security_issues: List[SecurityIssue]
    performance_metrics: List[PerformanceMetric]
    style_violations: List[CodeStyle]
    overall_score: float
    recommendations: List[str]
    approval_status: str
    reviewer_comments: str

@dataclass
class CodeMetrics:
    lines_of_code: int
    comment_lines: int
    complexity: Dict[str, int]
    dependencies: List[str]
    maintainability_index: float
    security_score: float
    performance_score: float

class Reviewer:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Reviewer with AI configuration."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize review templates
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
    async def analyze_code_metrics(self, code: str) -> CodeMetrics:
        """Calculate code metrics for analysis."""
        try:
            tree = ast.parse(code)
            
            # Count lines
            lines = code.split('\n')
            total_lines = len(lines)
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            
            # Calculate complexity
            complexity = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    complexity[node.name] = self._calculate_complexity(node)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(code)
            
            # Calculate maintainability index
            maintainability = self._calculate_maintainability(
                total_lines, 
                comment_lines,
                sum(complexity.values())
            )
            
            # Calculate security and performance scores
            security_score = self._analyze_security(tree)
            performance_score = self._analyze_performance(tree)
            
            return CodeMetrics(
                lines_of_code=total_lines,
                comment_lines=comment_lines,
                complexity=complexity,
                dependencies=dependencies,
                maintainability_index=maintainability,
                security_score=security_score,
                performance_score=performance_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing code metrics: {str(e)}")
            raise

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract code dependencies."""
        dependencies = set()
        patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'require\s*\(\s*[\'"](.+?)[\'"]\s*\)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code)
            dependencies.update(match.group(1) for match in matches)
        
        return list(dependencies)

    def _calculate_maintainability(self, 
                                 total_lines: int, 
                                 comment_lines: int, 
                                 complexity: int) -> float:
        """Calculate maintainability index."""
        if total_lines == 0:
            return 0.0
            
        # Maintainability Index formula
        comment_ratio = comment_lines / total_lines
        complexity_per_line = complexity / total_lines
        
        # Weighted calculation (based on common industry standards)
        maintainability = (
            100 - (complexity_per_line * 25) +
            (comment_ratio * 15) -
            (math.log(total_lines) * 10)
        )
        
        return max(0.0, min(100.0, maintainability))

    def _analyze_security(self, tree: ast.AST) -> float:
        """Analyze code for security issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Check for hardcoded credentials
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id.lower()
                        if any(word in name for word in ['password', 'secret', 'key', 'token']):
                            issues.append(SecurityIssue(
                                severity="high",
                                category="credentials",
                                description="Potential hardcoded credentials",
                                location=f"Line {node.lineno}",
                                recommendation="Use environment variables or secure storage",
                                cwe_id="CWE-798"
                            ))
            
            # Check for unsafe eval/exec
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append(SecurityIssue(
                            severity="critical",
                            category="code_injection",
                            description="Use of eval/exec is dangerous",
                            location=f"Line {node.lineno}",
                            recommendation="Avoid using eval/exec",
                            cwe_id="CWE-95"
                        ))
            
            # Check for SQL injection vulnerabilities
            if isinstance(node, ast.Call):
                if hasattr(node, 'func') and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'executemany']:
                        issues.append(SecurityIssue(
                            severity="high",
                            category="sql_injection",
                            description="Potential SQL injection vulnerability",
                            location=f"Line {node.lineno}",
                            recommendation="Use parameterized queries",
                            cwe_id="CWE-89"
                        ))
        
        # Calculate security score based on issues
        if not issues:
            return 100.0
            
        deductions = {
            "low": 5,
            "medium": 10,
            "high": 20,
            "critical": 40
        }
        
        score = 100.0
        for issue in issues:
            score -= deductions.get(issue.severity, 10)
        
        return max(0.0, score)

    def _analyze_performance(self, tree: ast.AST) -> float:
        """Analyze code for performance issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Check for nested loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child != node:
                        issues.append(PerformanceMetric(
                            category="complexity",
                            value=1.0,
                            unit="nested_loops",
                            threshold=0.0,
                            status="warning",
                            recommendation="Consider restructuring nested loops for better performance"
                        ))
            
            # Check for large data structures
            if isinstance(node, ast.List) or isinstance(node, ast.Dict):
                if len(node.elts) > 1000:
                    issues.append(PerformanceMetric(
                        category="memory",
                        value=float(len(node.elts)),
                        unit="elements",
                        threshold=1000.0,
                        status="warning",
                        recommendation="Large data structure might impact memory usage"
                    ))
            
            # Check for multiple database queries
            if isinstance(node, ast.Call):
                if hasattr(node, 'func') and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'query', 'find']:
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.For) and node in ast.walk(parent):
                                issues.append(PerformanceMetric(
                                    category="database",
                                    value=1.0,
                                    unit="query_in_loop",
                                    threshold=0.0,
                                    status="warning",
                                    recommendation="Consider using batch queries instead of queries in loops"
                                ))
        
        # Calculate performance score based on issues
        if not issues:
            return 100.0
            
        deductions = {
            "info": 2,
            "warning": 5,
            "error": 15,
            "critical": 30
        }
        
        score = 100.0
        for issue in issues:
            score -= deductions.get(issue.status, 5)
        
        return max(0.0, score)

    async def review_code(self, 
                         code: str, 
                         file_path: str,
                         context: Optional[Dict[str, Any]] = None) -> ReviewSummary:
        """Perform comprehensive code review."""
        try:
            # Calculate metrics
            metrics = await self.analyze_code_metrics(code)
            
            # Analyze code with AI
            review_prompt = f"""Review this code for quality, security, and performance:

            File: {file_path}
            Code:
            {code}

            Context:
            {json.dumps(context, indent=2) if context else 'No additional context'}

            Metrics:
            {json.dumps(metrics.__dict__, indent=2)}

            Focus on:
            1. Code quality and maintainability
            2. Security vulnerabilities
            3. Performance optimizations
            4. Style guide compliance
            5. Best practices
            6. Error handling
            7. Documentation
            8. Test coverage

            Provide specific recommendations for improvements.
            """

            review_response = await self.client.generate_content(review_prompt)
            review_data = json.loads(review_response.text)
            
            # Parse findings
            findings = []
            for finding in review_data.get('findings', []):
                findings.append(ReviewFinding(**finding))
            
            # Generate review summary
            return ReviewSummary(
                timestamp=datetime.now(),
                commit_id=context.get('commit_id') if context else None,
                files_reviewed=[file_path],
                total_findings=len(findings),
                security_issues=[f for f in findings if f.category == 'security'],
                performance_metrics=[f for f in findings if f.category == 'performance'],
                style_violations=[f for f in findings if f.category == 'style'],
                overall_score=self._calculate_overall_score(findings, metrics),
                recommendations=review_data.get('recommendations', []),
                approval_status=self._determine_approval_status(findings, metrics),
                reviewer_comments=review_data.get('comments', '')
            )
            
        except Exception as e:
            logger.error(f"Error reviewing code: {str(e)}")
            raise

    def _calculate_overall_score(self, 
                               findings: List[ReviewFinding], 
                               metrics: CodeMetrics) -> float:
        """Calculate overall code quality score."""
        # Base score from metrics
        base_score = (
            metrics.maintainability_index * 0.3 +
            metrics.security_score * 0.4 +
            metrics.performance_score * 0.3
        )
        
        # Deductions for findings
        deductions = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }
        
        for finding in findings:
            base_score -= deductions.get(finding.severity, 0)
        
        return max(0.0, min(100.0, base_score))

    def _determine_approval_status(self, 
                                 findings: List[ReviewFinding], 
                                 metrics: CodeMetrics) -> str:
        """Determine if code should be approved."""
        # Critical criteria
        if any(f.severity == 'critical' for f in findings):
            return 'rejected'
            
        if metrics.security_score < 70:
            return 'rejected'
            
        # Warning criteria
        if len([f for f in findings if f.severity in ['high', 'critical']]) > 3:
            return 'needs_revision'
            
        if metrics.maintainability_index < 60:
            return 'needs_revision'
            
        # Approval criteria
        if (metrics.security_score >= 80 and 
            metrics.maintainability_index >= 70 and 
            metrics.performance_score >= 75):
            return 'approved'
            
        return 'needs_revision'

    def save_review(self, 
                   review: ReviewSummary,
                   base_dir: str):
        """Save review results."""
        try:
            base_path = Path(base_dir)
            reviews_dir = base_path / "reviews"
            reviews_dir.mkdir(exist_ok=True)
            
            # Generate review filename
            timestamp = review.timestamp.strftime("%Y%m%d_%H%M%S")
            review_file = reviews_dir / f"review_{timestamp}.md"
            
            with review_file.open('w') as f:
                recommendations = "\n".join(f"- {rec}" for rec in review.recommendations)
                f.write(f"""# Code Review Summary
                
## Overview
- **Timestamp:** {review.timestamp}
- **Commit:** {review.commit_id or 'N/A'}
- **Files Reviewed:** {', '.join(review.files_reviewed)}
- **Overall Score:** {review.overall_score:.2f}/100
- **Status:** {review.approval_status.upper()}

## Security Issues ({len(review.security_issues)})
{"".join(f'''
- **{issue.severity.upper()}:** {issue.description}
  - Location: {issue.location}
  - Recommendation: {issue.recommendation}
  - CWE: {issue.cwe_id or 'N/A'}
''' for issue in review.security_issues)}

## Performance Metrics
{"".join(f'''
- **{metric.category}:** {metric.value} {metric.unit}
  - Status: {metric.status}
  - Recommendation: {metric.recommendation}
''' for metric in review.performance_metrics)}

## Style Violations ({len(review.style_violations)})
{"".join(f'''
- **{violation.severity}:** {violation.rule}
  - Location: {violation.location}
  - Suggestion: {violation.suggestion}
''' for violation in review.style_violations)}

## Recommendations
{recommendations}

## Reviewer Comments
{review.reviewer_comments}
""")
            
            logger.info(f"Review saved to {review_file}")
            
        except Exception as e:
            logger.error(f"Error saving review: {str(e)}")
            raise

@click.command()
@click.option('--commit-summary', required=True, help='Path to the commit summary file')
@click.option('--code-dir', required=True, help='Directory containing the code to review')
@click.option('--output', required=True, help='Path to save the review report')
def main(commit_summary: str, code_dir: str, output: str):
    """Review code and generate comprehensive report."""
    try:
        reviewer = Reviewer()
        
        # Load commit summary for context
        context = {
            "commit_summary": reviewer.load_file(commit_summary)
        }
        
        code_reviews = []
        coverage_analyses = {}
        security_findings = []
        style_issues = []
        
        # Review each Python file in the code directory recursively
        for root, _, files in os.walk(code_dir):
            for filename in files:
                if filename.endswith('.py') and not filename.startswith('test_'):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, code_dir)
                    test_path = os.path.join(root, f"test_{filename}")
                    
                    logger.info(f"Reviewing {relative_path}...")
                    
                    # Load code and tests
                    code = reviewer.load_file(file_path)
                    tests = reviewer.load_file(test_path) if os.path.exists(test_path) else ""
                    
                    # Add file context
                    file_context = {**context, "file": relative_path}
                    
                    # Perform reviews
                    review_results, approved = reviewer.review_code(code, file_context)
                    code_reviews.extend(review_results)
                    
                    coverage_analysis = reviewer.analyze_test_coverage(code, tests)
                    coverage_analyses[relative_path] = coverage_analysis
                    
                    security_audit = reviewer.security_audit(code)
                    security_findings.extend(security_audit)
                    
                    style_check = reviewer.style_check(code)
                    style_issues.extend(style_check)
                    
                    logger.info(f"Completed review of {relative_path}")
        
        # Generate and save review report
        report = reviewer._generate_review_report(
            code_reviews,
            coverage_analyses.get(next(iter(coverage_analyses), ''), {}),
            security_findings,
            style_issues
        )
        reviewer.save_file(output, report)
        
        logger.info(f"Successfully generated review report: {output}")
        
    except Exception as e:
        logger.error(f"Failed to generate review: {str(e)}")
        raise

if __name__ == '__main__':
    main()
