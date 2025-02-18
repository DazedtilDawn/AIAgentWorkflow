import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_pro():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try with gemini-pro
        model = genai.GenerativeModel('gemini-pro')
        
        # Test simple completion
        response = model.generate_content("Say hello!")
        print("\nResponse from Gemini Pro:")
        print(response.text)
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_pro()
