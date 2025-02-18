"""
Tests for the AI agents in the automated software development framework.
"""
import sys
import os
import pytest
import pathlib
from dotenv import load_dotenv
import logging
from unittest.mock import AsyncMock, Mock
import json

# Set up logging
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import after path setup
from ai_agents.product_manager import (
    ProductManager, 
    ProductSpecification,
    UserPersona,
    MarketContext,
    FeatureSpecification
)
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

class MockResponse:
    """Mock Gemini API response."""
    def __init__(self, text):
        self.text = text
        
    async def __call__(self, *args, **kwargs):
        return self

    def __await__(self):
        async def _async_result():
            return self
        return _async_result().__await__()

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
    prompt = "Build a task management system with AI-powered prioritization"
    
    # Mock Gemini response for market context
    mock_market_context = {
        "target_market": "Software development teams",
        "competitors": ["Jira", "Trello"],
        "trends": ["AI integration", "Automation"],
        "demographics": "Tech-savvy professionals",
        "pain_points": ["Manual prioritization", "Context switching"],
        "opportunities": ["AI-driven insights", "Workflow automation"]
    }
    
    # Mock Gemini response for user personas
    mock_personas = [{
        "name": "Tech Lead Sarah",
        "role": "Development Team Lead",
        "goals": ["Improve team productivity"],
        "challenges": ["Task prioritization"],
        "preferences": ["Clean UI"],
        "tech_proficiency": "Expert"
    }]
    
    # Mock Gemini response for features
    mock_features = [{
        "name": "AI Task Prioritization",
        "description": "Automatically prioritize tasks using ML",
        "priority": "high",
        "requirements": ["ML model integration", "Task scoring system"],
        "acceptance_criteria": ["Tasks are correctly prioritized"]
    }]
    
    # Mock Gemini response for product specs
    mock_specs = {
        "title": "AI Task Manager",
        "description": "Task management with AI prioritization",
        "market_context": mock_market_context,
        "features": mock_features
    }
    
    # Configure mocks
    mock_responses = [
        MockResponse(json.dumps(mock_market_context)),  # For market context
        MockResponse(json.dumps(mock_personas)),        # For user personas
        MockResponse(json.dumps(mock_features)),        # For features
        MockResponse(json.dumps(mock_specs))           # For final specs
    ]
    
    product_manager.client.generate_content = AsyncMock(side_effect=mock_responses)
    
    try:
        specs = await product_manager.create_product_specs(prompt)
        logger.info(f"Generated specs: {specs}")
        assert isinstance(specs, ProductSpecification)
        assert specs.title is not None
        assert len(specs.features) > 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.debug(f"Mock responses: {mock_responses}")
        raise

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
