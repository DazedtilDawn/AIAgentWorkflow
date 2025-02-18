import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

try:
    # Configure the library
    genai.configure(api_key=api_key)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-pro')
    
    # Generate a response
    response = model.generate_content('Write "Hello, World!"')
    
    print("\nResponse from Gemini:")
    print(response.text)
    
except Exception as e:
    print(f"\nError: {str(e)}")
