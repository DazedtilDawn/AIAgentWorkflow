import click
import os
import json
from loguru import logger
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import asyncio
import ast
from dataclasses import dataclass
import re

class CodeQuality(BaseModel):
    complexity: int
    maintainability_index: float
    documentation_coverage: float
    test_coverage: float
    security_score: float
    performance_score: float

class TestCase(BaseModel):
    name: str
    description: str
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    mocks: Dict[str, Any] = Field(default_factory=dict)

class UnitTest(TestCase):
    test_type: str = "unit"
    isolation_level: str
    mocked_dependencies: List[str]

class IntegrationTest(TestCase):
    test_type: str = "integration"
    components: List[str]
    data_flows: List[Dict[str, Any]]

class E2ETest(TestCase):
    test_type: str = "e2e"
    user_flow: List[str]
    environment_setup: Dict[str, Any]
    cleanup_steps: List[str]

@dataclass
class CodeAnalysis:
    imports: List[str]
    classes: List[str]
    functions: List[str]
    dependencies: List[str]
    complexity: Dict[str, int]
    potential_issues: List[str]

class CodeImplementation(BaseModel):
    file_path: str
    code_content: str
    language: str
    dependencies: List[str]
    quality_metrics: CodeQuality
    tests: List[Union[UnitTest, IntegrationTest, E2ETest]]
    documentation: Dict[str, str]
    commit_message: str
    review_status: Optional[Dict[str, Any]] = None

class Engineer:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Engineer with AI configuration and development tools."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize test templates directory
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
    async def analyze_code(self, code: str) -> CodeAnalysis:
        """Analyze code structure and complexity."""
        try:
            tree = ast.parse(code)
            
            # Extract imports
            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
            imports.extend([f"{node.module}.{name.name}" for node in ast.walk(tree) 
                          if isinstance(node, ast.ImportFrom) for name in node.names])
            
            # Extract classes and functions
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Calculate complexity
            complexity = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    complexity[node.name] = self._calculate_complexity(node)
            
            # Identify potential issues
            issues = self._identify_code_issues(tree)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(code)
            
            return CodeAnalysis(
                imports=imports,
                classes=classes,
                functions=functions,
                dependencies=dependencies,
                complexity=complexity,
                potential_issues=issues
            )
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            raise

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a code block."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _identify_code_issues(self, tree: ast.AST) -> List[str]:
        """Identify potential code issues and anti-patterns."""
        issues = []
        
        for node in ast.walk(tree):
            # Check for overly complex functions
            if isinstance(node, ast.FunctionDef):
                if self._calculate_complexity(node) > 10:
                    issues.append(f"High complexity in function {node.name}")
                    
            # Check for large try-except blocks
            if isinstance(node, ast.Try):
                if len(node.body) > 15:
                    issues.append("Large try-except block detected")
                    
            # Check for multiple returns
            if isinstance(node, ast.FunctionDef):
                returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
                if returns > 3:
                    issues.append(f"Multiple return statements in {node.name}")
        
        return issues

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract external dependencies from code."""
        dependencies = set()
        
        # Regular expressions for different import patterns
        import_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'require\s*\(\s*[\'"](.+?)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, code)
            dependencies.update(match.group(1) for match in matches)
        
        return list(dependencies)

    async def generate_component_code(self, 
                                   component_spec: Dict[str, Any], 
                                   architecture: Dict[str, Any],
                                   existing_code: Optional[str] = None) -> CodeImplementation:
        """Generate implementation code for a component with tests."""
        try:
            # Prepare the context
            context = {
                "spec": component_spec,
                "architecture": architecture,
                "existing_code": existing_code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Generate implementation code
            implementation_prompt = f"""Generate production-ready implementation code for this component:

            Component Specification:
            {json.dumps(component_spec, indent=2)}

            System Architecture:
            {json.dumps(architecture, indent=2)}

            Existing Code (if any):
            {existing_code if existing_code else 'No existing code'}

            Requirements:
            1. Follow clean code principles
            2. Implement proper error handling
            3. Add comprehensive documentation
            4. Include input validation
            5. Add logging
            6. Follow security best practices
            7. Optimize for performance
            8. Include type hints
            9. Follow PEP 8 style guide

            Return the implementation as a JSON object with:
            1. code_content: The actual code
            2. file_path: Suggested file path
            3. language: Programming language
            4. dependencies: Required dependencies
            5. documentation: API docs and usage examples
            """

            implementation_response = await self.client.generate_content(implementation_prompt)
            implementation_data = json.loads(implementation_response.text)
            
            # Generate tests
            test_prompt = f"""Create comprehensive tests for this implementation:

            Implementation:
            {implementation_data['code_content']}

            Component Specification:
            {json.dumps(component_spec, indent=2)}

            Create:
            1. Unit tests for each function/method
            2. Integration tests for component interactions
            3. End-to-end tests for user flows
            4. Edge cases and error scenarios
            5. Performance benchmarks

            Format as JSON array of test objects (UnitTest, IntegrationTest, or E2ETest).
            """

            test_response = await self.client.generate_content(test_prompt)
            test_data = json.loads(test_response.text)
            
            # Parse test data into appropriate test objects
            tests = []
            for test in test_data:
                if test["test_type"] == "unit":
                    tests.append(UnitTest(**test))
                elif test["test_type"] == "integration":
                    tests.append(IntegrationTest(**test))
                else:
                    tests.append(E2ETest(**test))
            
            # Calculate quality metrics
            quality_prompt = f"""Analyze this implementation for quality metrics:

            Code:
            {implementation_data['code_content']}

            Tests:
            {json.dumps(test_data, indent=2)}

            Calculate:
            1. Code complexity
            2. Maintainability index
            3. Documentation coverage
            4. Test coverage
            5. Security score
            6. Performance score

            Return as JSON object matching CodeQuality model.
            """

            quality_response = await self.client.generate_content(quality_prompt)
            quality_data = json.loads(quality_response.text)
            
            # Generate commit message
            commit_prompt = f"""Create a descriptive commit message for these changes:

            Component: {component_spec.get('name', 'Unknown Component')}
            Changes:
            1. New implementation
            2. Added {len(tests)} tests
            3. Quality metrics: {json.dumps(quality_data, indent=2)}

            Follow conventional commit format.
            """

            commit_response = await self.client.generate_content(commit_prompt)
            
            # Create and return CodeImplementation
            return CodeImplementation(
                file_path=implementation_data["file_path"],
                code_content=implementation_data["code_content"],
                language=implementation_data["language"],
                dependencies=implementation_data["dependencies"],
                quality_metrics=CodeQuality(**quality_data),
                tests=tests,
                documentation=implementation_data["documentation"],
                commit_message=commit_response.text.strip()
            )

        except Exception as e:
            logger.error(f"Error generating component code: {str(e)}")
            raise

    async def implement_features(self, plan_file: str, arch_file: str) -> str:
        """Wrapper method for integration test compatibility."""
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = f.read()
            with open(arch_file, 'r', encoding='utf-8') as f:
                architecture = f.read()
            
            # Call the actual implementation method
            implementation = await self.generate_component_code(
                json.loads(plan),
                json.loads(architecture)
            )
            return implementation.code_content
            
        except Exception as e:
            logger.error(f"Error in implement_features: {str(e)}")
            raise

    async def generate_test_code(self, 
                               implementation: CodeImplementation,
                               test_case: TestCase) -> str:
        """Generate test code for a specific test case."""
        try:
            test_prompt = f"""Generate test code for this test case:

            Implementation:
            {implementation.code_content}

            Test Case:
            {json.dumps(test_case.dict(), indent=2)}

            Requirements:
            1. Use appropriate testing framework
            2. Include all necessary imports
            3. Implement setup and teardown
            4. Add clear assertions
            5. Handle edge cases
            6. Mock external dependencies
            7. Add performance benchmarks
            8. Include error case testing
            """

            response = await self.client.generate_content(test_prompt)
            return response.text

        except Exception as e:
            logger.error(f"Error generating test code: {str(e)}")
            raise

    def save_implementation(self, 
                          implementation: CodeImplementation,
                          base_dir: str):
        """Save implementation code and tests."""
        try:
            base_path = Path(base_dir)
            
            # Save main implementation
            impl_path = base_path / implementation.file_path
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            
            with impl_path.open('w') as f:
                f.write(implementation.code_content)
            
            # Save tests
            test_dir = impl_path.parent / "tests"
            test_dir.mkdir(exist_ok=True)
            
            for test in implementation.tests:
                test_path = test_dir / f"test_{impl_path.stem}_{test.name}.py"
                
                with test_path.open('w') as f:
                    f.write(f"""\"\"\"
Test: {test.name}
Description: {test.description}
Type: {test.test_type}
\"\"\"
import pytest
from typing import Dict, Any
import json
import asyncio
from pathlib import Path

# Test setup
{test.setup_code if test.setup_code else '# No setup required'}

# Test implementation
def test_{test.name}():
    # Arrange
    inputs = {json.dumps(test.inputs, indent=4)}
    expected = {json.dumps(test.expected_outputs, indent=4)}
    
    # Act
    # TODO: Implement test logic
    
    # Assert
    # TODO: Add assertions

# Test teardown
{test.teardown_code if test.teardown_code else '# No teardown required'}
""")
            
            # Save documentation
            docs_dir = impl_path.parent / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            with (docs_dir / f"{impl_path.stem}_api.md").open('w') as f:
                f.write(implementation.documentation.get("api", ""))
            
            with (docs_dir / f"{impl_path.stem}_usage.md").open('w') as f:
                f.write(implementation.documentation.get("usage", ""))
            
            # Save quality report
            with (docs_dir / f"{impl_path.stem}_quality.md").open('w') as f:
                f.write(f"""# Code Quality Report

## Metrics
- Complexity: {implementation.quality_metrics.complexity}
- Maintainability Index: {implementation.quality_metrics.maintainability_index}
- Documentation Coverage: {implementation.quality_metrics.documentation_coverage}%
- Test Coverage: {implementation.quality_metrics.test_coverage}%
- Security Score: {implementation.quality_metrics.security_score}
- Performance Score: {implementation.quality_metrics.performance_score}

## Tests
Total Tests: {len(implementation.tests)}
- Unit Tests: {len([t for t in implementation.tests if isinstance(t, UnitTest)])}
- Integration Tests: {len([t for t in implementation.tests if isinstance(t, IntegrationTest)])}
- E2E Tests: {len([t for t in implementation.tests if isinstance(t, E2ETest)])}

## Dependencies
{chr(10).join(f'- {dep}' for dep in implementation.dependencies)}

## Review Status
{json.dumps(implementation.review_status, indent=2) if implementation.review_status else 'Not reviewed yet'}
""")
            
            # Save commit summary
            with (base_path / "COMMIT_SUMMARY.md").open('a') as f:
                f.write(f"""
## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{implementation.commit_message}

### Files Changed
- {implementation.file_path}
- {len(implementation.tests)} test files
- Documentation and quality reports

### Quality Metrics
- Complexity: {implementation.quality_metrics.complexity}
- Test Coverage: {implementation.quality_metrics.test_coverage}%
- Security Score: {implementation.quality_metrics.security_score}
""")
            
            logger.info(f"Implementation saved to {impl_path}")
            
        except Exception as e:
            logger.error(f"Error saving implementation: {str(e)}")
            raise

@click.command()
@click.argument('plan', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
async def main(plan: str, output_dir: str):
    """Generate implementation code and tests based on the development plan."""
    try:
        # Read development plan
        with open(plan, 'r') as f:
            plan_data = json.load(f)
        
        # Initialize engineer
        engineer = Engineer()
        
        # Process each component
        for component in plan_data.get("components", []):
            # Generate implementation
            implementation = await engineer.generate_component_code(
                component,
                plan_data.get("architecture", {})
            )
            
            # Save implementation and tests
            engineer.save_implementation(implementation, output_dir)
            
        logger.info(f"Implementation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in implementation generation: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
