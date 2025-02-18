import pytest
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

def pytest_configure(config):
    """Configure pytest environment."""
    # Load environment variables
    load_dotenv()
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    
    # Ensure required environment variables are set
    required_vars = ["GEMINI_API_KEY"]
    for var in required_vars:
        if var not in os.environ:
            raise EnvironmentError(f"Required environment variable {var} is not set")
    
    # Create necessary directories if they don't exist
    required_dirs = ["docs", "src/tests", "ai_agents"]
    for dir_path in required_dirs:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent

@pytest.fixture(scope="session")
def docs_dir(project_root):
    """Return the docs directory."""
    return project_root / "docs"

@pytest.fixture(scope="session")
def src_dir(project_root):
    """Return the src directory."""
    return project_root / "src"

@pytest.fixture(scope="session")
def ai_agents_dir(project_root):
    """Return the ai_agents directory."""
    return project_root / "ai_agents"

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run end-to-end tests"
    )

def pytest_collection_modifyitems(config, items):
    """Skip end-to-end tests unless --run-e2e is specified."""
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)
