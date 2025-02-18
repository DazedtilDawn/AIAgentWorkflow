import os
from typing import Dict, Any, Optional
from google.generativeai import types, GenerativeModel, configure
from loguru import logger
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the base agent with Gemini configuration."""
        self.model = model
        
        # Configure Gemini with API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Initialize the model
        configure(api_key=api_key)
        self.client = GenerativeModel(self.model)
        
        # Test the configuration
        try:
            response = self.client.generate_content("Test connection")
            logger.info("Successfully connected to Gemini API")
        except Exception as e:
            logger.error(f"Failed to connect to Gemini API: {str(e)}")
            raise
    
    async def get_completion(self, 
                           prompt: str, 
                           system_message: Optional[str] = None,
                           temperature: float = 0.7) -> str:
        """Get completion from Gemini API with error handling."""
        try:
            # Combine system message and prompt if provided
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            
            response = self.client.generate_content(
                contents=full_prompt,
                generation_config=types.GenerationConfig(
                    temperature=temperature
                )
            )
            
            # Check if the response has content
            if not response.text:
                raise Exception("No response generated")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            raise
    
    def load_file(self, filepath: str) -> str:
        """Safely load file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {str(e)}")
            raise
    
    def save_file(self, filepath: str, content: str) -> None:
        """Safely save content to file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {str(e)}")
            raise
            
    def validate_file_exists(self, filepath: str) -> bool:
        """Validate that a required file exists."""
        if not os.path.exists(filepath):
            logger.error(f"Required file not found: {filepath}")
            return False
        return True
