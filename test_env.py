import os
import pathlib
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    # Get the directory containing this script
    current_dir = pathlib.Path(__file__).parent.absolute()
    env_path = current_dir / '.env'
    
    print(f"Looking for .env at: {env_path}")
    print(f"File exists: {env_path.exists()}")
    
    # Load environment variables from local .env
    load_dotenv(dotenv_path=env_path)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
        
    print(f"API key found (length: {len(api_key)})")
        
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-001")
        
        # Test simple completion
        response = model.generate_content("Hello!")
        print("✅ Successfully connected to Gemini API")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error connecting to Gemini: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_connection()
