import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import google.generativeai as genai
import pathlib
from loguru import logger
import json
from pydantic import BaseModel
import datetime

class ValidationResult(BaseModel):
    is_approved: bool
    issues: List[str] = []
    suggestions: List[str] = []

class RoleFeedback(BaseModel):
    concerns: List[str]
    suggestions: List[str]

class ApprovalSystem:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the approval system with Gemini configuration."""
        self.model = model
        
        # Load environment variables from local .env
        current_dir = pathlib.Path(__file__).parent.parent.absolute()
        env_path = current_dir / '.env'
        load_dotenv(dotenv_path=env_path)
        
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY environment variable not set")
            
        # Initialize Gemini
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Test connection
        try:
            response = self.client.generate_content("Test connection")
            logger.info("Successfully connected to Gemini API")
        except Exception as e:
            logger.error(f"Failed to connect to Gemini API: {str(e)}")
            raise
    
    async def validate_product_specs(self, specs: Dict[str, Any]) -> ValidationResult:
        """Validate product specifications."""
        prompt = f"""Validate the following product specifications for completeness and clarity:

        {json.dumps(specs, indent=2)}

        Consider:
        1. Are all required fields present and properly defined?
        2. Is the scope clear and well-bounded?
        3. Are success metrics measurable and relevant?
        4. Are technical requirements specific and achievable?
        5. Are constraints realistic and well-defined?

        Format response as JSON with fields:
        - is_approved: boolean
        - issues: list of strings
        - suggestions: list of strings
        """
        
        try:
            response = await self.client.generate_content(prompt)
            validation = json.loads(response.text)
            return ValidationResult(**validation)
        except Exception as e:
            logger.error(f"Error validating product specs: {str(e)}")
            return ValidationResult(
                is_approved=False,
                issues=[f"Validation error: {str(e)}"],
                suggestions=["Please review and fix the specifications format"]
            )
    
    async def validate_architecture(self, architecture: Dict[str, Any], specs: Dict[str, Any]) -> ValidationResult:
        """Validate system architecture against product specifications."""
        prompt = f"""Validate the following system architecture against the product specifications:

        Product Specifications:
        {json.dumps(specs, indent=2)}

        System Architecture:
        {json.dumps(architecture, indent=2)}

        Consider:
        1. Does the architecture satisfy all requirements?
        2. Are the technology choices appropriate?
        3. Are all components and their interactions well-defined?
        4. Are security and scalability properly addressed?
        5. Does it align with best practices and patterns?

        Format response as JSON with fields:
        - is_approved: boolean
        - issues: list of strings
        - suggestions: list of strings
        """
        
        try:
            response = await self.client.generate_content(prompt)
            validation = json.loads(response.text)
            return ValidationResult(**validation)
        except Exception as e:
            logger.error(f"Error validating architecture: {str(e)}")
            return ValidationResult(
                is_approved=False,
                issues=[f"Validation error: {str(e)}"],
                suggestions=["Please review and fix the architecture format"]
            )
    
    async def cross_validate_with_role(self, 
                                     content: Dict[str, Any], 
                                     role: str,
                                     context: Optional[Dict[str, Any]] = None) -> RoleFeedback:
        """Cross-validate content with another role's perspective."""
        # Add context if provided
        context_str = f"\nAdditional Context:\n{json.dumps(context, indent=2)}" if context else ""
        prompt = f"""From the perspective of a {role}, review this content:

        {json.dumps(content, indent=2)}
        {context_str}

        Provide feedback considering your role's specific concerns and expertise.
        Format response as JSON with fields:
        - concerns: list of strings (specific issues or potential problems)
        - suggestions: list of strings (constructive improvements)
        """
        
        try:
            response = await self.client.generate_content(prompt)
            feedback = json.loads(response.text)
            return RoleFeedback(**feedback)
        except Exception as e:
            logger.error(f"Error in cross-validation with {role}: {str(e)}")
            return RoleFeedback(
                concerns=[f"Cross-validation error: {str(e)}"],
                suggestions=["Please retry the validation process"]
            )
    
    def save_validation_report(self, 
                             result: ValidationResult,
                             artifact_type: str,
                             artifact_id: str) -> str:
        """Save validation results to a report file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = pathlib.Path("docs/validation_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"{artifact_type}_{artifact_id}_{timestamp}.json"
        
        with open(report_path, "w") as f:
            json.dump(result.dict(), f, indent=2)
        
        logger.info(f"Validation report saved to {report_path}")
        return str(report_path)
