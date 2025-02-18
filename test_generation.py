import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyBo-xBUjefiuV9fmjmn3ILzApwiS9Scyps")

# Create a model instance
model = genai.GenerativeModel('gemini-2.0-flash-001')

# Generate content
response = model.generate_content("Write a short greeting!")
print(response.text)
