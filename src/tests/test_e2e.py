import pytest
from playwright.sync_api import Page
import os
from pathlib import Path

def test_documentation_files_exist():
    """Test that all required documentation files exist."""
    docs_dir = Path("docs")
    required_files = [
        "PRODUCT_SPECS.md",
        "SYSTEM_ARCHITECTURE.md",
        "PLAN.md",
        "BRAINSTORM_OUTCOME.md",
        "REVIEW.md",
        "DOCUMENTATION.md"
    ]
    
    for file in required_files:
        assert (docs_dir / file).exists(), f"{file} is missing"

def test_project_structure():
    """Test that the project structure is correct."""
    required_dirs = [
        "ai_agents",
        "docs",
        "src",
        "scripts",
        ".github/workflows"
    ]
    
    for dir_path in required_dirs:
        assert Path(dir_path).exists(), f"{dir_path} directory is missing"

def test_environment_variables():
    """Test that required environment variables are set."""
    required_vars = [
        "GEMINI_API_KEY"
    ]
    
    for var in required_vars:
        assert var in os.environ, f"{var} environment variable is not set"

@pytest.mark.skip(reason="Requires running server")
def test_web_interface(page: Page):
    """Test the web interface if applicable."""
    page.goto("http://localhost:3000")
    
    # Check for key elements
    assert page.is_visible("text=AI Agent Workflow")
    
    # Test navigation
    page.click("text=Documentation")
    assert page.url.endswith("/documentation")
    
    # Test agent interaction
    page.fill("[data-testid=prompt-input]", "Create a simple web app")
    page.click("[data-testid=submit-button]")
    
    # Wait for response
    page.wait_for_selector("[data-testid=response-output]")
    response_text = page.text_content("[data-testid=response-output]")
    assert len(response_text) > 0

def test_github_workflow():
    """Test that GitHub workflow file is properly configured."""
    workflow_file = Path(".github/workflows/multi-role-pipeline.yml")
    assert workflow_file.exists()
    
    content = workflow_file.read_text()
    required_jobs = [
        "product-manager",
        "architect",
        "engineer",
        "reviewer",
        "qa-engineer"
    ]
    
    for job in required_jobs:
        assert job in content.lower(), f"{job} job is missing from workflow"
