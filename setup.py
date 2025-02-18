from setuptools import setup, find_packages

setup(
    name="ai_agents",
    version="3.2.0",
    description="AI-Driven Development Framework with Gemini 2.0 Flash",
    author="AI Agent Workflow Team",
    packages=find_packages(),
    install_requires=[
        # Google AI dependencies
        "google-generativeai",
        
        # Core dependencies
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "playwright>=1.40.0",
        "boto3>=1.29.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "loguru>=0.7.2",
    ],
    python_requires=">=3.9",
)
