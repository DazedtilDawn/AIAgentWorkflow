import os
from dotenv import load_dotenv
import subprocess

def test_curl():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API key not found")
        return
        
    # Construct the curl command
    curl_command = [
        'curl',
        f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}',
        '-H', 'Content-Type: application/json',
        '-X', 'POST',
        '-d', '{\"contents\": [{\"parts\":[{\"text\": \"Explain how AI works\"}]}]}'
    ]
    
    try:
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        print("\nResponse:")
        print(result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_curl()
