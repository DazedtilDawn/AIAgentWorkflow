"""
Tests for the AI agents in the automated software development framework.
"""
import sys
import os
import pytest
import pathlib
from dotenv import load_dotenv
import logging
from unittest.mock import AsyncMock, Mock, MagicMock
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
    
    def mock_generate_content(*args, **kwargs):
        """Mock the Gemini API response with predefined test data."""
        mock_response = MagicMock()
        
        # Get the prompt from either args or kwargs
        prompt = kwargs.get('contents', '') if kwargs else args[0] if args else ''
        system_message = kwargs.get('system_message', '')
        
        logger.debug(f"[Mock] Received prompt: {prompt[:200]}")
        logger.debug(f"[Mock] System message: {system_message[:200]}")
        
        # Analyze the combined prompt to determine response type
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        logger.debug(f"[Mock] Full prompt: {full_prompt[:200]}")
        
        if "market context" in full_prompt.lower():
            logger.debug("[Mock] Generating market context response")
            mock_response.text = json.dumps({
                "target_market": "Software development teams",
                "competitors": ["Jira", "Trello"],
                "trends": ["AI integration", "Automation"],
                "demographics": "Tech-savvy professionals",
                "pain_points": ["Manual prioritization", "Context switching"],
                "opportunities": ["AI-driven insights", "Workflow automation"]
            }, indent=2)
        elif "user personas" in full_prompt.lower():
            logger.debug("[Mock] Generating user personas response")
            mock_response.text = json.dumps([{
                "name": "Tech Lead Sarah",
                "role": "Development Team Lead",
                "goals": ["Improve team productivity"],
                "challenges": ["Task prioritization"],
                "preferences": ["Clean UI"],
                "tech_proficiency": "Expert"
            }], indent=2)
        elif "features" in full_prompt.lower():
            logger.debug("[Mock] Generating features response")
            mock_response.text = json.dumps([
                # Minimal valid feature
                {
                    "name": "Basic Feature",
                    "description": "Simple feature",
                    "priority": "low",
                    "requirements": [],
                    "acceptance_criteria": []
                },
                # Feature with all optional fields
                {
                    "name": "Complex Feature",
                    "description": "Detailed feature description",
                    "priority": "high",
                    "requirements": ["Req1", "Req2"],
                    "acceptance_criteria": ["AC1", "AC2"],
                    "technical_requirements": ["Tech1", "Tech2"],
                    "dependencies": ["Dep1"],
                    "estimated_effort": "High",
                    "risks": ["Risk1", "Risk2"],
                    "additional_notes": "Some notes"
                }
            ], indent=2)
        else:
            logger.warning(f"[Mock] No matching response type for prompt: {full_prompt[:100]}")
            mock_response.text = "{}"
            
        logger.debug(f"[Mock] Generated response: {mock_response.text[:200]}")
        return mock_response
    
    product_manager.client.generate_content = AsyncMock(side_effect=mock_generate_content)
    
    try:
        specs = await product_manager.create_product_specs(prompt)
        logger.info(f"Generated specs: {specs}")
        assert isinstance(specs, ProductSpecification)
        assert specs.title is not None
        assert len(specs.features) > 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
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

@pytest.mark.asyncio
async def test_feature_validation_edge_cases(product_manager):
    """Test feature validation with various edge cases."""
    def mock_generate_content(*args, **kwargs):
        """Mock the Gemini API response with predefined test data."""
        mock_response = MagicMock()
        
        # Get the prompt from either args or kwargs
        prompt = kwargs.get('contents', '') if kwargs else args[0] if args else ''
        system_message = kwargs.get('system_message', '')
        
        logger.debug(f"[Mock] Received prompt: {prompt[:200]}")
        logger.debug(f"[Mock] System message: {system_message[:200]}")
        
        # Analyze the combined prompt to determine response type
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        logger.debug(f"[Mock] Full prompt: {full_prompt[:200]}")
        
        if "market context" in full_prompt.lower():
            logger.debug("[Mock] Generating market context response")
            mock_response.text = json.dumps({
                "target_market": "Software developers",
                "competitors": ["Competitor1", "Competitor2"],
                "trends": ["Trend1", "Trend2"],
                "demographics": "Tech professionals",
                "pain_points": ["Pain1", "Pain2"],
                "opportunities": ["Opp1", "Opp2"]
            }, indent=2)
        elif "user personas" in full_prompt.lower():
            logger.debug("[Mock] Generating user personas response")
            mock_response.text = json.dumps([{
                "name": "Test User",
                "role": "Developer",
                "goals": ["Goal1"],
                "challenges": ["Challenge1"],
                "preferences": ["Pref1"],
                "tech_proficiency": "Expert"
            }], indent=2)
        elif "features" in full_prompt.lower():
            logger.debug("[Mock] Generating features response")
            mock_response.text = json.dumps([
                # Minimal valid feature
                {
                    "name": "Basic Feature",
                    "description": "Simple feature",
                    "priority": "low",
                    "requirements": [],
                    "acceptance_criteria": []
                },
                # Feature with all optional fields
                {
                    "name": "Complex Feature",
                    "description": "Detailed feature description",
                    "priority": "high",
                    "requirements": ["Req1", "Req2"],
                    "acceptance_criteria": ["AC1", "AC2"],
                    "technical_requirements": ["Tech1", "Tech2"],
                    "dependencies": ["Dep1"],
                    "estimated_effort": "High",
                    "risks": ["Risk1", "Risk2"],
                    "additional_notes": "Some notes"
                }
            ], indent=2)
        else:
            logger.warning(f"[Mock] No matching response type for prompt: {full_prompt[:100]}")
            mock_response.text = "{}"
            
        logger.debug(f"[Mock] Generated response: {mock_response.text[:200]}")
        return mock_response
    
    product_manager.client.generate_content = AsyncMock(side_effect=mock_generate_content)
    
    try:
        specs = await product_manager.create_product_specs("Test edge cases")
        logger.info(f"Edge case specs: {specs}")
        
        # Validate market context
        assert specs.market_context.target_market == "Software developers"
        assert len(specs.market_context.competitors) == 2
        assert len(specs.market_context.trends) == 2
        
        # Validate user personas
        assert len(specs.audience) == 1
        assert specs.audience[0].name == "Test User"
        assert specs.audience[0].tech_proficiency == "Expert"
        
        # Validate minimal feature
        minimal_feature = specs.features[0]
        assert minimal_feature.name == "Basic Feature"
        assert minimal_feature.priority == "low"
        assert isinstance(minimal_feature.requirements, list)
        assert isinstance(minimal_feature.acceptance_criteria, list)
        
        # Validate complex feature
        complex_feature = specs.features[1]
        assert complex_feature.name == "Complex Feature"
        assert complex_feature.priority == "high"
        assert len(complex_feature.technical_requirements) == 2
        assert len(complex_feature.dependencies) == 1
        assert complex_feature.estimated_effort == "High"
        assert len(complex_feature.risks) == 2
    except Exception as e:
        logger.error(f"Edge case test failed: {str(e)}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_invalid_feature_handling(product_manager):
    """Test handling of invalid feature data."""
    def mock_generate_content(*args, **kwargs):
        """Mock the Gemini API response with predefined test data."""
        mock_response = MagicMock()
        
        # Get the prompt from either args or kwargs
        prompt = kwargs.get('contents', '') if kwargs else args[0] if args else ''
        system_message = kwargs.get('system_message', '')
        
        logger.debug(f"[Mock] Received prompt: {prompt[:200]}")
        logger.debug(f"[Mock] System message: {system_message[:200]}")
        
        # Analyze the combined prompt to determine response type
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        logger.debug(f"[Mock] Full prompt: {full_prompt[:200]}")
        
        if "market context" in full_prompt.lower():
            logger.debug("[Mock] Generating market context response")
            mock_response.text = json.dumps({
                "target_market": "Test Market",
                "competitors": ["Comp1"],
                "trends": ["Trend1"],
                "demographics": "Test Demo",
                "pain_points": ["Pain1"],
                "opportunities": ["Opp1"]
            }, indent=2)
        elif "user personas" in full_prompt.lower():
            logger.debug("[Mock] Generating user personas response")
            mock_response.text = json.dumps([{
                "name": "Test User",
                "role": "Tester",
                "goals": ["Goal1"],
                "challenges": ["Challenge1"],
                "preferences": ["Pref1"],
                "tech_proficiency": "Intermediate"
            }], indent=2)
        elif "features" in full_prompt.lower():
            # Generate invalid feature data
            mock_response.text = json.dumps([
                {
                    "name": "",  # Empty name
                    "description": "Invalid feature",
                    "priority": "invalid_priority",  # Invalid priority
                    "requirements": None,  # Invalid requirements
                    "acceptance_criteria": "Not a list"  # Invalid format
                }
            ], indent=2)
        else:
            logger.warning(f"[Mock] No matching response type for prompt: {full_prompt[:100]}")
            mock_response.text = "{}"
            
        logger.debug(f"[Mock] Generated response: {mock_response.text[:200]}")
        return mock_response
    
    product_manager.client.generate_content = AsyncMock(side_effect=mock_generate_content)
    
    try:
        with pytest.raises(ValueError) as exc_info:
            await product_manager.create_product_specs("Test invalid features")
        
        logger.info(f"Expected validation error: {str(exc_info.value)}")
        assert "validation error" in str(exc_info.value).lower()
    except Exception as e:
        logger.error(f"Invalid feature test failed: {str(e)}", exc_info=True)
        raise
