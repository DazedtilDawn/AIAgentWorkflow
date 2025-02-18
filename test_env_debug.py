import os
from dotenv import load_dotenv
import pathlib

def debug_env():
    # Get current directory
    current_dir = pathlib.Path(__file__).parent.absolute()
    env_path = current_dir / '.env'
    
    print(f"Looking for .env at: {env_path}")
    print(f"File exists: {env_path.exists()}")
    
    # Try to load .env
    load_dotenv(dotenv_path=env_path)
    
    # Print all environment variables starting with VITE_
    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        if key.startswith('VITE_'):
            print(f"{key}: {'*' * len(value)}")  # Hide actual value for security

if __name__ == "__main__":
    debug_env()
