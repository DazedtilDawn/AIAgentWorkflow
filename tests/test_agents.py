"""
Tests for the AI agents in the automated software development framework.
"""
import sys
import os
import pytest
import pathlib
from dotenv import load_dotenv

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import after path setup
from ai_agents.product_manager import ProductManager
from ai_agents.approval_system import ApprovalSystem
from ai_agents.checkpoint_system import CheckpointSystem

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Ensure API key is available
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def approval_system():
    """Fixture for the approval system."""
    return ApprovalSystem()

@pytest.fixture
def checkpoint_system(approval_system):
    """Fixture for the checkpoint system."""
    return CheckpointSystem(approval_system)

@pytest.fixture
def product_manager():
    """Fixture for the product manager."""
    return ProductManager()

@pytest.mark.asyncio
async def test_product_manager_initialization(product_manager):
    """Test that the product manager initializes correctly."""
    assert product_manager.approval_system is not None
    assert product_manager.checkpoint_system is not None

@pytest.mark.asyncio
async def test_create_product_specs(product_manager):
    """Test creating product specifications."""
    prompt = "Create a web-based task management system"
    specs = await product_manager.create_product_specs(prompt)
    
    # Verify required fields
    assert "title" in specs
    assert "description" in specs
    assert "scope" in specs
    assert "audience" in specs
    assert "success_metrics" in specs
    assert "technical_requirements" in specs
    assert "constraints" in specs
    assert "timeline" in specs
    
    # Verify content quality
    assert len(specs["title"]) > 0
    assert len(specs["description"]) > 0
    assert isinstance(specs["scope"], dict)
    assert isinstance(specs["audience"], list)
    assert isinstance(specs["success_metrics"], list)
    assert isinstance(specs["technical_requirements"], list)
    assert isinstance(specs["constraints"], list)
    assert isinstance(specs["timeline"], dict)

@pytest.mark.asyncio
async def test_approval_system_validation(approval_system):
    """Test the approval system's validation capabilities."""
    test_specs = {
        "title": "Test Project",
        "description": "A test project for validation",
        "scope": {
            "features": ["Feature 1", "Feature 2"],
            "limitations": ["Limitation 1"]
        },
        "audience": ["User Type 1", "User Type 2"],
        "success_metrics": ["Metric 1", "Metric 2"],
        "technical_requirements": ["Requirement 1"],
        "constraints": ["Constraint 1"],
        "timeline": {
            "phases": ["Phase 1", "Phase 2"],
            "estimated_duration": "3 months"
        }
    }
    
    validation_result = await approval_system.validate_product_specs(test_specs)
    assert validation_result is not None
    assert hasattr(validation_result, "is_approved")
    assert hasattr(validation_result, "issues")
    assert hasattr(validation_result, "suggestions")

@pytest.mark.asyncio
async def test_checkpoint_system(checkpoint_system):
    """Test the checkpoint system's functionality."""
    # Create a checkpoint
    checkpoint_id = "test_checkpoint"
    stage = "product_specs"
    checkpoint = checkpoint_system.create_checkpoint(checkpoint_id, stage)
    
    assert checkpoint.checkpoint_id == checkpoint_id
    assert checkpoint.stage == stage
    assert checkpoint.status == "pending"
    
    # Test validation
    test_content = {
        "title": "Test Project",
        "description": "A test project",
        "scope": {"features": ["Feature 1"]},
        "audience": ["User 1"],
        "success_metrics": ["Metric 1"],
        "technical_requirements": ["Requirement 1"],
        "constraints": ["Constraint 1"],
        "timeline": {"phases": ["Phase 1"]}
    }
    
    validation_roles = ["Architect", "Engineer"]
    validated_checkpoint = await checkpoint_system.validate_checkpoint(
        checkpoint_id,
        test_content,
        validation_roles
    )
    
    assert validated_checkpoint.status in ["approved", "rejected"]
    assert validated_checkpoint.validation_result is not None
    if validated_checkpoint.status == "rejected":
        assert validated_checkpoint.blocking_issues is not None
