import pytest
import os
from ai_agents.product_manager import ProductManager
from ai_agents.architect import Architect
from ai_agents.engineer import Engineer
from ai_agents.qa_engineer import QAEngineer
from ai_agents.reviewer import Reviewer

@pytest.mark.asyncio
async def test_full_development_cycle():
    """Test the complete development cycle from requirements to review."""
    
    # Initialize all agents
    pm = ProductManager(model="gemini-2.0-flash")
    architect = Architect(model="gemini-2.0-flash")
    engineer = Engineer(model="gemini-2.0-flash")
    qa = QAEngineer(model="gemini-2.0-flash")
    reviewer = Reviewer(model="gemini-2.0-flash")
    
    # 1. Generate product specifications
    requirements = "Create a simple web application that displays current weather"
    specs = await pm.generate_product_specs(requirements)
    assert isinstance(specs, str)
    assert "weather" in specs.lower()
    
    # 2. Generate system design
    design = await architect.generate_system_design(specs)
    assert isinstance(design, str)
    assert len(design) > 0
    
    # 3. Generate implementation plan
    plan = await engineer.generate_implementation_plan(design)
    assert isinstance(plan, dict)
    assert "tasks" in plan
    
    # 4. Generate test scenarios
    test_scenarios = await qa.generate_test_scenarios("src", design)
    assert isinstance(test_scenarios, list)
    assert len(test_scenarios) > 0
    
    # 5. Generate code review
    review = await reviewer.review_code("src", design)
    assert isinstance(review, dict)
    assert "feedback" in review

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling across all agents."""
    
    pm = ProductManager(model="gemini-2.0-flash")
    
    # Test with invalid input
    with pytest.raises(ValueError):
        await pm.generate_product_specs("")
    
    # Test with missing dependencies
    with pytest.raises(ImportError):
        await pm.generate_product_specs(None)

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple agents working concurrently."""
    
    pm = ProductManager(model="gemini-2.0-flash")
    architect = Architect(model="gemini-2.0-flash")
    
    # Run multiple operations concurrently
    requirements = ["Create a web app", "Create a mobile app", "Create a desktop app"]
    
    async def process_requirement(req):
        specs = await pm.generate_product_specs(req)
        design = await architect.generate_system_design(specs)
        return specs, design
    
    # Run all requirements concurrently
    results = await asyncio.gather(*[process_requirement(req) for req in requirements])
    
    assert len(results) == len(requirements)
    for specs, design in results:
        assert isinstance(specs, str)
        assert isinstance(design, str)
