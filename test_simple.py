import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyBo-xBUjefiuV9fmjmn3ILzApwiS9Scyps")

# List available models
for m in genai.list_models():
    print(m.name)
