import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_models():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        print("\nAvailable Models:")
        for m in genai.list_models():
            print(f"- {m.name}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    list_models()
