import pytest
from ai_agents.planner import Planner

@pytest.fixture
def planner():
    return Planner()

def test_planner_initialization(planner):
    """Test that the planner initializes correctly."""
    assert planner.model == "gemini-2.0-flash"

@pytest.mark.asyncio
async def test_generate_plan(planner):
    """Test plan generation with mock inputs."""
    product_specs = {
        "title": "Test Project",
        "description": "A test project for planning",
        "features": [
            {
                "name": "Feature 1",
                "description": "Test feature",
                "priority": "high"
            }
        ]
    }
    
    architecture = {
        "tech_stack": ["python", "pytest"],
        "components": ["planner", "executor"],
        "patterns": ["strategy", "observer"]
    }
    
    plan = await planner.generate_plan(product_specs, architecture)
    assert isinstance(plan, dict)
    assert "tasks" in plan
    assert "dependencies" in plan
    assert "timeline" in plan
