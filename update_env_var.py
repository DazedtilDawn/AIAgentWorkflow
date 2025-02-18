import os
import re

def update_env_var_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace in string literals and error messages
    content = content.replace('VITE_GEMINI_API_KEY', 'GEMINI_API_KEY')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of directories to search in
    search_dirs = [
        'ai_agents',
        'tests',
        'src/tests',
    ]
    
    # Files to update
    for search_dir in search_dirs:
        dir_path = os.path.join(base_dir, search_dir)
        if not os.path.exists(dir_path):
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    update_env_var_in_file(file_path)
    
    # Update .env file if it exists
    env_file = os.path.join(base_dir, '.env')
    if os.path.exists(env_file):
        update_env_var_in_file(env_file)
    
    # Update individual test files in root directory
    test_files = [
        'test_vite.py',
        'test_safety.py',
        'test_json.py',
    ]
    
    for test_file in test_files:
        file_path = os.path.join(base_dir, test_file)
        if os.path.exists(file_path):
            update_env_var_in_file(file_path)

if __name__ == '__main__':
    main()
