import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

def test_json_response():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key not found")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Simple prompt requesting JSON
    prompt = """
    Return a simple JSON object like this:
    {
        "message": "hello",
        "number": 42
    }
    
    IMPORTANT: Response must be valid JSON only. No other text.
    """
    
    try:
        response = model.generate_content(prompt)
        print("Raw response:")
        print(response.text)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_json_response()
