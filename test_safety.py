import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

def test_safety_model():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key not found")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models
    print("Available models:")
    for m in genai.list_models():
        print(f"- {m.name}")
    
    # Try with gemini-pro first
    print("\nTesting with gemini-pro:")
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = """Return a simple JSON object like this:
    {
        "message": "hello",
        "number": 42
    }
    
    IMPORTANT: Response must be valid JSON only. No other text.
    """
    
    try:
        response = model.generate_content(prompt)
        print("\nRaw response:")
        print(response.text)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_safety_model()
