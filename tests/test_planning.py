import pytest
import asyncio
from ai_agents.planner import Planner
from loguru import logger
import json
import os
import google.generativeai as genai
import inspect

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def planner():
    """Initialize planner."""
    return Planner()

def test_planner_initialization(planner):
    """Test that the planner initializes correctly."""
    # Log available methods
    logger.info("Available Planner methods:")
    for name, method in inspect.getmembers(planner, predicate=inspect.ismethod):
        logger.info(f"Method: {name}")
    
    # Log environment info
    logger.info(f"Running on OS: {os.name}")
    logger.info(f"Python path: {os.environ.get('PYTHONPATH', 'Not set')}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    assert planner.model == "gemini-2.0-flash"
    assert os.getenv("GEMINI_API_KEY") is not None, "GEMINI_API_KEY environment variable not set"

@pytest.mark.asyncio
@pytest.mark.timeout(60)  # Set timeout per test
async def test_generate_plan(planner):
    """Test plan generation with mock inputs."""
    logger.info("Starting test_generate_plan")
    
    # Log planner state
    logger.info("Planner methods at test start:")
    for name, method in inspect.getmembers(planner, predicate=inspect.ismethod):
        logger.info(f"Method: {name}")
    
    # Test simple content generation first
    try:
        logger.info("Testing basic content generation...")
        # Create a test model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Say 'hello world'")
        logger.info(f"Basic response: {response.text}")
    except Exception as e:
        logger.error(f"Error in basic content generation: {str(e)}")
        raise

    # If basic test passes, continue with full test
    product_specs = {
        "title": "Test Project",
        "description": "A test project for planning",
        "features": [{"name": "Feature 1", "description": "Test feature", "priority": "high"}]
    }
    
    architecture = {
        "tech_stack": ["python", "pytest"],
        "components": ["planner", "executor"],
        "patterns": ["strategy", "observer"]
    }
    
    try:
        plan = await planner.generate_development_plan(
            specs=json.dumps(product_specs),
            architecture=json.dumps(architecture)
        )
        assert isinstance(plan, dict)
        assert "tasks" in plan
        assert "dependencies" in plan
        assert "timeline" in plan
    except Exception as e:
        logger.error(f"Error in plan generation: {str(e)}")
        raise
