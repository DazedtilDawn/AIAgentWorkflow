import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

def test_models():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    
    try:
        # Configure the library
        genai.configure(api_key=api_key)
        
        # List available models
        print("\nAvailable Models:")
        for m in genai.list_models():
            print(f"- {m.name}")
        
        # Try both model versions
        models_to_test = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-001",
            "gemini-pro"
        ]
        
        for model_name in models_to_test:
            print(f"\nTesting model: {model_name}")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say hello!")
                print(f"Response: {response.text}")
            except Exception as e:
                print(f"Error with {model_name}: {str(e)}")
        
    except Exception as e:
        print(f"\nGlobal Error: {str(e)}")

if __name__ == "__main__":
    test_models()
