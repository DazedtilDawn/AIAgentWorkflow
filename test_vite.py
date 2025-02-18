import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

def test_gemini():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize with Flash model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test simple completion
        response = model.generate_content("Say hello!")
        print("\nResponse from Gemini Flash:")
        print(response.text)
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_gemini()
