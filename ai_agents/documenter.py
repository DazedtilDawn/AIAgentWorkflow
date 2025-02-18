import click
from loguru import logger
import google.generativeai as genai
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import re
from datetime import datetime
from dataclasses import dataclass
import yaml

@dataclass
class APIEndpoint:
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Any]
    examples: List[Dict[str, Any]]

@dataclass
class ComponentDoc:
    name: str
    description: str
    dependencies: List[str]
    public_api: List[str]
    usage_examples: List[str]
    configuration: Dict[str, Any]

@dataclass
class ChangelogEntry:
    version: str
    date: datetime
    changes: List[Dict[str, Any]]
    breaking_changes: List[str]
    migration_guide: Optional[str]

class Documenter:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Documenter with AI configuration."""
        self.model = model
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize documentation directory
        self.docs_dir = Path(__file__).parent.parent / "docs"
        self.docs_dir.mkdir(exist_ok=True)

    async def generate_documentation(self, 
                                  architecture_file: str, 
                                  code_files: list) -> str:
        """Generate comprehensive documentation based on architecture and code."""
        try:
            # Load architecture and code files
            architecture = self.load_file(architecture_file)
            code_contents = []
            for file in code_files:
                try:
                    content = self.load_file(file)
                    code_contents.append(f"File: {file}\n{content}")
                except Exception as e:
                    logger.warning(f"Could not load file {file}: {str(e)}")
            
            # Prepare the prompt
            system_message = """You are a Technical Documentation Specialist responsible for creating
            comprehensive, clear, and well-structured documentation. Focus on making the documentation
            accessible to developers while maintaining technical accuracy."""
            
            prompt = f"""{system_message}

            Based on this system architecture:
            {architecture}

            And these code files:
            {''.join(code_contents)}

            Generate comprehensive documentation including:
            1. Overview
               - System purpose and goals
               - Key features and capabilities
               - Technology stack
               - Architecture overview
            
            2. System Architecture
               - Component breakdown
               - Data flow diagrams
               - Integration points
               - Security considerations
            
            3. Component Documentation
               - Purpose and responsibilities
               - Dependencies and relationships
               - Configuration options
               - Usage examples
            
            4. API Reference
               - Endpoints and methods
               - Request/response formats
               - Authentication
               - Rate limiting
            
            5. Setup Guide
               - Prerequisites
               - Installation steps
               - Configuration
               - Environment setup
            
            6. Deployment Instructions
               - Deployment options
               - Environment variables
               - Infrastructure requirements
               - Monitoring setup
            
            7. Troubleshooting Guide
               - Common issues
               - Debug procedures
               - Logging and monitoring
               - Support resources
            
            8. Development Workflow
               - Code organization
               - Testing strategy
               - CI/CD pipeline
               - Contributing guidelines
            """
            
            # Get completion from the model
            response = await self.client.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            raise

    async def generate_api_documentation(self, 
                                      code_files: List[str],
                                      api_spec: Optional[Dict] = None) -> List[APIEndpoint]:
        """Generate API documentation with examples and best practices."""
        try:
            # Load code files
            code_contents = []
            for file in code_files:
                try:
                    content = self.load_file(file)
                    code_contents.append(f"File: {file}\n{content}")
                except Exception as e:
                    logger.warning(f"Could not load file {file}: {str(e)}")
            
            # Prepare API context
            api_context = f"API Specification:\n{json.dumps(api_spec, indent=2)}\n" if api_spec else ""
            
            # Generate documentation
            system_message = """You are an API Documentation Specialist focusing on creating
            clear, accurate, and developer-friendly API documentation."""
            
            prompt = f"""{system_message}

            Based on these code files:
            {''.join(code_contents)}

            {api_context}
            Generate comprehensive API documentation including:
            1. Endpoint specifications
               - Path and method
               - Description and purpose
               - Parameters and types
               - Response formats
               - Authentication requirements
            
            2. Usage examples
               - Request examples
               - Response examples
               - Error scenarios
               - Rate limiting
            
            3. Best practices
               - Security considerations
               - Performance optimization
               - Error handling
               - Versioning strategy
            
            Return the documentation in a structured format that can be parsed into APIEndpoint objects.
            """
            
            response = await self.client.generate_content(prompt)
            return self._parse_api_documentation(response.text)
            
        except Exception as e:
            logger.error(f"Error generating API documentation: {str(e)}")
            raise

    async def generate_component_documentation(self, 
                                           component_files: Dict[str, str],
                                           architecture: Optional[Dict] = None) -> List[ComponentDoc]:
        """Generate detailed component documentation."""
        try:
            # Prepare component context
            arch_context = f"Architecture:\n{json.dumps(architecture, indent=2)}\n" if architecture else ""
            
            # Generate documentation
            system_message = """You are a Component Documentation Specialist focusing on creating
            clear and comprehensive component documentation."""
            
            prompt = f"""{system_message}

            {arch_context}
            For these components:
            {json.dumps(component_files, indent=2)}

            Generate detailed component documentation including:
            1. Component overview
               - Purpose and responsibilities
               - Design principles
               - Dependencies
            
            2. Public API
               - Methods and functions
               - Parameters and return types
               - Usage patterns
            
            3. Configuration
               - Required settings
               - Optional parameters
               - Environment variables
            
            4. Integration
               - Dependencies
               - Event handling
               - Error scenarios
            
            5. Examples
               - Usage examples
               - Integration examples
               - Configuration examples
            
            Return the documentation in a structured format that can be parsed into ComponentDoc objects.
            """
            
            response = await self.client.generate_content(prompt)
            return self._parse_component_documentation(response.text)
            
        except Exception as e:
            logger.error(f"Error generating component documentation: {str(e)}")
            raise

    async def generate_changelog(self,
                              current_version: str,
                              previous_version: str,
                              changes: List[Dict[str, Any]]) -> ChangelogEntry:
        """Generate a detailed changelog with migration guide."""
        try:
            system_message = """You are a Release Documentation Specialist focusing on creating
            clear and informative changelogs with migration guidance."""
            
            prompt = f"""
            Generate a detailed changelog for version {current_version} (previous: {previous_version})
            based on these changes:

            {json.dumps(changes, indent=2)}

            Include:
            1. Version and date
            2. Changes by category
               - Features
               - Improvements
               - Bug fixes
               - Performance
            3. Breaking changes
            4. Migration guide
            5. Upgrade steps
            
            Return in a format that can be parsed into a ChangelogEntry object.
            """
            
            response = await self.client.generate_content(prompt)
            return self._parse_changelog(response.text, current_version)
            
        except Exception as e:
            logger.error(f"Error generating changelog: {str(e)}")
            raise

    async def update_cursor_rules(self,
                               documentation: str,
                               existing_rules: Optional[str] = None) -> str:
        """Update .cursorrules based on documentation insights."""
        try:
            system_message = """You are a Development Tools Expert updating IDE rules
            to maintain documentation quality and consistency."""
            
            context = f"Existing rules:\n{existing_rules}\n" if existing_rules else ""
            prompt = f"""{context}
            Based on this documentation:

            {documentation}

            Generate updated .cursorrules that:
            1. Enforce documentation standards
               - Required sections
               - Format consistency
               - Example inclusion
            
            2. Maintain API documentation
               - Parameter documentation
               - Return type documentation
               - Error handling documentation
            
            3. Component documentation
               - Purpose documentation
               - Dependency documentation
               - Configuration documentation
            
            4. Code examples
               - Usage examples
               - Error handling examples
               - Configuration examples
            """
            
            response = await self.client.generate_content(prompt)
            return self._format_cursor_rules(response.text)
            
        except Exception as e:
            logger.error(f"Error updating cursor rules: {str(e)}")
            raise

    def save_file(self, content: str, filepath: str) -> None:
        """Save content to a file, creating directories if needed."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Successfully saved file: {filepath}")
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {str(e)}")
            raise

    def load_file(self, filepath: str) -> str:
        """Load content from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {str(e)}")
            raise

    def _parse_api_documentation(self, raw_docs: str) -> List[APIEndpoint]:
        """Parse raw API documentation into structured format."""
        try:
            endpoints = []
            current_endpoint = None
            
            for line in raw_docs.split('\n'):
                if line.startswith('Endpoint:'):
                    if current_endpoint:
                        endpoints.append(current_endpoint)
                    current_endpoint = {}
                elif current_endpoint is not None:
                    if line.startswith('  Path:'):
                        current_endpoint['path'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Method:'):
                        current_endpoint['method'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Description:'):
                        current_endpoint['description'] = line.split(':', 1)[1].strip()
                    # Add more parsing logic for parameters, responses, etc.
            
            if current_endpoint:
                endpoints.append(current_endpoint)
            
            return [APIEndpoint(**endpoint) for endpoint in endpoints]
            
        except Exception as e:
            logger.error(f"Error parsing API documentation: {str(e)}")
            raise

    def _parse_component_documentation(self, raw_docs: str) -> List[ComponentDoc]:
        """Parse raw component documentation into structured format."""
        try:
            components = []
            current_component = None
            
            for line in raw_docs.split('\n'):
                if line.startswith('Component:'):
                    if current_component:
                        components.append(current_component)
                    current_component = {}
                elif current_component is not None:
                    if line.startswith('  Name:'):
                        current_component['name'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Description:'):
                        current_component['description'] = line.split(':', 1)[1].strip()
                    # Add more parsing logic for dependencies, API, etc.
            
            if current_component:
                components.append(current_component)
            
            return [ComponentDoc(**component) for component in components]
            
        except Exception as e:
            logger.error(f"Error parsing component documentation: {str(e)}")
            raise

    def _parse_changelog(self, raw_changelog: str, version: str) -> ChangelogEntry:
        """Parse raw changelog into structured format."""
        try:
            # Extract sections using regex
            changes_section = re.search(r"Changes:(.*?)(?=Breaking Changes:|$)", 
                                     raw_changelog, re.DOTALL)
            breaking_section = re.search(r"Breaking Changes:(.*?)(?=Migration Guide:|$)", 
                                      raw_changelog, re.DOTALL)
            migration_section = re.search(r"Migration Guide:(.*?)(?=$)", 
                                       raw_changelog, re.DOTALL)
            
            # Parse changes into categories
            changes = []
            if changes_section:
                for line in changes_section.group(1).strip().split('\n'):
                    if line.strip():
                        category = "other"
                        if "feature:" in line.lower():
                            category = "feature"
                        elif "fix:" in line.lower():
                            category = "fix"
                        elif "improvement:" in line.lower():
                            category = "improvement"
                        changes.append({
                            "category": category,
                            "description": line.strip()
                        })
            
            # Parse breaking changes
            breaking_changes = []
            if breaking_section:
                breaking_changes = [line.strip() 
                                 for line in breaking_section.group(1).strip().split('\n')
                                 if line.strip()]
            
            return ChangelogEntry(
                version=version,
                date=datetime.now(),
                changes=changes,
                breaking_changes=breaking_changes,
                migration_guide=migration_section.group(1).strip() if migration_section else None
            )
            
        except Exception as e:
            logger.error(f"Error parsing changelog: {str(e)}")
            raise

    def _format_cursor_rules(self, raw_rules: str) -> str:
        """Format rules into .cursorrules format."""
        try:
            # Parse the rules into a structured format
            rules_dict = yaml.safe_load(raw_rules)
            
            # Convert to .cursorrules format
            formatted_rules = []
            
            for category, rules in rules_dict.items():
                formatted_rules.append(f"# {category}")
                for rule in rules:
                    formatted_rules.append(f"- pattern: {rule['pattern']}")
                    formatted_rules.append(f"  message: {rule['message']}")
                    formatted_rules.append(f"  severity: {rule['severity']}")
                formatted_rules.append("")
            
            return "\n".join(formatted_rules)
            
        except Exception as e:
            logger.error(f"Error formatting cursor rules: {str(e)}")
            raise

@click.command()
@click.option('--architecture-file', required=True, help='Path to the system architecture file')
@click.option('--code-dir', required=True, help='Directory containing code files to document')
@click.option('--output', required=True, help='Output file path for documentation')
def main(architecture_file: str, code_dir: str, output: str):
    """Generate comprehensive documentation using the Documenter agent."""
    try:
        documenter = Documenter()
        
        # Get all Python files in the code directory
        code_files = []
        for root, _, files in os.walk(code_dir):
            for file in files:
                if file.endswith('.py'):
                    code_files.append(os.path.join(root, file))
        
        # Generate documentation
        documentation = documenter.generate_documentation(architecture_file, code_files)
        
        # Save to file
        documenter.save_file(documentation, output)
        logger.info(f"Successfully generated documentation: {output}")
        
    except Exception as e:
        logger.error(f"Failed to generate documentation: {str(e)}")
        raise

if __name__ == '__main__':
    main()
