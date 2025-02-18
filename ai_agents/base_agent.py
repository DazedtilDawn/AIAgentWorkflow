import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from functools import wraps
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("ACTIONS_STEP_DEBUG") else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_hook(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"ENTRY: {func.__name__} - args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"EXIT: {func.__name__} - result: {result}")
            return result
        except Exception as e:
            logger.error(f"ERROR: {func.__name__} - {str(e)}")
            raise
    return wrapper

class BaseAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the base agent with Gemini configuration."""
        self.model = model
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self._validate_and_configure()
        self.client = genai.GenerativeModel(model)
        
    @debug_hook
    def _validate_and_configure(self):
        """Validate and configure the Gemini API."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        try:
            logger.info("Successfully configured Gemini API")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
    
    @debug_hook
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
                generation_config=genai.GenerationConfig(
                    temperature=temperature
                )
            )
            
            # Check if the response has content
            if not response.candidates:
                raise Exception("No response generated")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            raise
    
    @debug_hook
    def load_file(self, filepath: str) -> str:
        """Safely load file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {str(e)}")
            raise
    
    @debug_hook
    def save_file(self, filepath: str, content: str) -> None:
        """Safely save content to file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {str(e)}")
            raise
            
    @debug_hook
    def validate_file_exists(self, filepath: str) -> bool:
        """Validate that a required file exists."""
        if not os.path.exists(filepath):
            logger.error(f"Required file not found: {filepath}")
            return False
        return True
