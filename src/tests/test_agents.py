import pytest
import sys
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
env_path = Path(project_root) / '.env'
load_dotenv(dotenv_path=env_path)

# Ensure API key is available
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set")

from ai_agents.product_manager import ProductManager
from ai_agents.architect import Architect
from ai_agents.engineer import Engineer
from ai_agents.qa_engineer import QAEngineer
from ai_agents.reviewer import Reviewer
from ai_agents.approval_system import ApprovalSystem
from ai_agents.checkpoint_system import CheckpointSystem

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)
pytestmark = pytest.mark.asyncio

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def approval_system():
    """Fixture for the approval system."""
    return ApprovalSystem(model="gemini-2.0-flash")

@pytest.fixture
def checkpoint_system(approval_system):
    """Fixture for the checkpoint system."""
    return CheckpointSystem(approval_system)

@pytest.fixture
def product_manager():
    """Fixture for the product manager."""
    return ProductManager(model="gemini-2.0-flash")

@pytest.fixture
def architect():
    """Fixture for the architect."""
    return Architect(model="gemini-2.0-flash")

@pytest.fixture
def engineer():
    """Fixture for the engineer."""
    return Engineer(model="gemini-2.0-flash")

@pytest.fixture
def qa_engineer():
    """Fixture for the QA engineer."""
    return QAEngineer(model="gemini-2.0-flash")

@pytest.fixture
def reviewer():
    """Fixture for the reviewer."""
    return Reviewer(model="gemini-2.0-flash")

@pytest.mark.asyncio
async def test_approval_system_initialization(approval_system):
    """Test that the approval system initializes correctly."""
    assert approval_system.model == "gemini-2.0-flash"
    assert approval_system.client is not None

@pytest.mark.asyncio
async def test_checkpoint_system_initialization(checkpoint_system):
    """Test that the checkpoint system initializes correctly."""
    assert checkpoint_system.approval_system is not None
    assert isinstance(checkpoint_system.checkpoints, dict)

@pytest.mark.asyncio
async def test_product_manager_initialization(product_manager):
    """Test that the product manager initializes correctly."""
    assert product_manager.approval_system is not None
    assert product_manager.checkpoint_system is not None

@pytest.mark.asyncio
async def test_architect_initialization(architect):
    """Test that the architect initializes correctly."""
    assert architect.model == "gemini-2.0-flash"
    assert architect.client is not None

@pytest.mark.asyncio
async def test_engineer_initialization(engineer):
    """Test that the engineer initializes correctly."""
    assert engineer.model == "gemini-2.0-flash"
    assert engineer.client is not None

@pytest.mark.asyncio
async def test_qa_engineer_initialization(qa_engineer):
    """Test that the QA engineer initializes correctly."""
    assert qa_engineer.model == "gemini-2.0-flash"
    assert qa_engineer.client is not None

@pytest.mark.asyncio
async def test_reviewer_initialization(reviewer):
    """Test that the reviewer initializes correctly."""
    assert reviewer.model == "gemini-2.0-flash"
    assert reviewer.client is not None

@pytest.mark.asyncio
async def test_product_manager_spec_generation(product_manager):
    """Test that the product manager can generate specifications."""
    prompt = "Create a simple web-based task management system"
    specs = await product_manager.create_product_specs(prompt)
    
    # Verify required fields
    assert isinstance(specs, dict)
    assert "title" in specs
    assert "description" in specs
    assert "scope" in specs
    assert "audience" in specs
    assert "success_metrics" in specs
    assert "technical_requirements" in specs
    assert "constraints" in specs
    assert "timeline" in specs

@pytest.mark.asyncio
async def test_architect_design_generation(architect):
    """Test that the architect can generate system design."""
    test_specs = {
        "title": "Test Project",
        "description": "A test project",
        "scope": {"features": ["Feature 1"]},
        "audience": ["User 1"],
        "success_metrics": ["Metric 1"],
        "technical_requirements": ["Requirement 1"],
        "constraints": ["Constraint 1"],
        "timeline": {"phases": ["Phase 1"]}
    }
    
    design = await architect.create_system_design(test_specs)
    assert isinstance(design, dict)
    assert "architecture" in design
    assert "tech_stack" in design
    assert "components" in design

@pytest.mark.asyncio
async def test_qa_engineer_test_generation(qa_engineer):
    """Test that the QA engineer can generate test scenarios."""
    test_code = """
    def add(a: int, b: int) -> int:
        return a + b
    """
    
    test_scenarios = await qa_engineer.generate_test_scenarios(
        code_dir="test_code",
        review_content="Basic arithmetic function that adds two integers"
    )
    
    assert isinstance(test_scenarios, list)
    assert len(test_scenarios) > 0
    for scenario in test_scenarios:
        assert isinstance(scenario, dict)
        assert "description" in scenario
