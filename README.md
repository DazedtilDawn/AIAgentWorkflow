# AI-Driven Development Framework

A comprehensive, advanced AI-driven software development framework that automates the entire development process using multiple specialized AI agents.

## Features

- **Multi-Agent Orchestration**: Specialized AI agents for different roles in the development lifecycle
- **GitHub Actions Integration**: Automated CI/CD pipeline with role-based stages
- **Gemini 2.0 Flash Integration**: High-performance AI completions for each agent
- **Comprehensive Testing**: Automated testing with UI/API validation
- **Cloud Integration**: AWS deployment and monitoring capabilities

## Agents

1. **Product Manager**: Generates product specifications from requirements
2. **Brainstorm Facilitator**: Manages ideation and solution evaluation
3. **Architect**: Creates system architecture and technical specifications
4. **Planner**: Generates detailed development plans
5. **Engineer**: Implements code and generates tests
6. **Reviewer**: Reviews code quality and test coverage
7. **QA Engineer**: Designs and runs comprehensive tests
8. **Monitoring Analyst**: Analyzes system metrics and user behavior
9. **Refactor Analyst**: Identifies code improvements and maintains quality

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - Required AWS credentials for deployment

## Usage

The framework can be run either through GitHub Actions or locally:

### GitHub Actions
Push to the main branch or create a pull request to trigger the pipeline.

### Local Development
Run individual agents:
```bash
python ai_agents/product_manager.py --output docs/PRODUCT_SPECS.md
python ai_agents/architect.py --input docs/PRODUCT_SPECS.md --output docs/SYSTEM_ARCHITECTURE.md
# ... and so on for other agents
```

## Project Structure

```
.
├── .github/
│   └── workflows/          # GitHub Actions workflow definitions
├── ai_agents/             # AI agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── product_manager.py # Product Manager agent
│   ├── architect.py       # Architect agent
│   └── ...                # Other agent implementations
├── docs/                  # Generated documentation and artifacts
├── scripts/              # Deployment and monitoring scripts
├── src/                  # Generated application code
└── tests/               # Test suites
```

## Troubleshooting

### Gemini API Integration

#### Common Issues and Solutions

1. **JSON Schema Validation Errors**
   - **Issue**: The Gemini model's response may not match the expected JSON schema
   - **Solution**: 
     - Use explicit JSON schema in the prompt
     - Clean the response text to remove markdown formatting
     - Implement manual JSON parsing with proper error handling
     ```python
     response_text = response.text.strip()
     if response_text.startswith("```json"):
         response_text = response_text[7:]
     if response_text.endswith("```"):
         response_text = response_text[:-3]
     response_text = response_text.strip()
     ```

2. **Response Schema Compatibility**
   - **Issue**: The `response_schema` feature may not be available or work as expected
   - **Solution**: 
     - Use manual JSON parsing with `json.loads()`
     - Validate against Pydantic models after parsing
     ```python
     try:
         specs_dict = json.loads(response_text)
         specs = ProductSpecification(**specs_dict)
     except json.JSONDecodeError:
         logger.error("Failed to parse response as JSON")
         raise ValueError("Model response was not valid JSON")
     ```

3. **String Formatting in Prompts**
   - **Issue**: f-strings with JSON examples can cause formatting errors
   - **Solution**: 
     - Use string concatenation instead of f-strings for JSON examples
     - Properly escape JSON in prompts
     ```python
     prompt = """
     Your instructions here...
     """ + json.dumps(data, indent=2) + """
     More instructions...
     """
     ```

4. **Model Selection**
   - **Issue**: Different models may have varying capabilities for structured output
   - **Solution**: 
     - Use the `gemini-2.0-flash` model for consistent JSON responses
     - Include explicit instructions to return only JSON
     - Add example JSON structure in the prompt

#### Best Practices

1. **Prompt Engineering**
   - Always include the exact JSON schema in the prompt
   - Request "Return ONLY the JSON object, nothing else"
   - Provide clear examples of expected output format

2. **Error Handling**
   - Implement comprehensive error handling for JSON parsing
   - Log both the raw response and cleaned response for debugging
   - Use try-except blocks to catch specific exceptions

3. **Response Validation**
   - Use Pydantic models to validate response structure
   - Implement cross-validation with multiple roles
   - Generate detailed validation reports

4. **Code Organization**
   - Separate prompt templates from main logic
   - Use consistent JSON schema across all agents
   - Implement proper logging for troubleshooting

### Example Implementation

Here's a complete example of handling Gemini API responses:

```python
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import google.generativeai as genai
from loguru import logger

class ProductSpecification(BaseModel):
    scope: Dict[str, Any]
    audience: Dict[str, Any]
    success_metrics: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    constraints: Dict[str, Any]

def generate_content(prompt: str, client: genai.GenerativeModel) -> Dict[str, Any]:
    try:
        # Generate content
        response = client.generate_content(prompt)
        
        # Clean response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse and validate
        try:
            specs_dict = json.loads(response_text)
            specs = ProductSpecification(**specs_dict)
            return specs.dict()
        except json.JSONDecodeError:
            logger.error(f"Failed to parse response as JSON: {response_text}")
            raise ValueError("Model response was not valid JSON")
        except Exception as e:
            logger.error(f"Failed to validate specs against schema: {str(e)}")
            raise ValueError("Response did not match required schema")
            
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise
```

This implementation includes:
- Proper response cleaning
- JSON parsing with error handling
- Schema validation using Pydantic
- Comprehensive logging
- Clear error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
