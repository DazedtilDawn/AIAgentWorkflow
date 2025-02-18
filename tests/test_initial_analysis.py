import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from ai_agents.base_agent import BaseAgent
from ai_agents.architect import Architect
from ai_agents.product_manager import ProductManager

def test_environment_setup():
    """Test that required environment variables are set."""
    assert os.getenv("GEMINI_API_KEY") is not None, "GEMINI_API_KEY environment variable not set"

def test_base_agent_initialization():
    """Test that BaseAgent can be initialized with default model."""
    agent = BaseAgent()
    assert agent.model == "gemini-2.0-flash"

@patch('google.generativeai.GenerativeModel')
def test_architect_initialization(mock_model):
    """Test that Architect can be initialized with default model."""
    mock_model.return_value = MagicMock()
    architect = Architect()
    assert architect.model == "gemini-2.0-flash"
    assert hasattr(architect, 'client'), "Architect should have a client attribute"

@patch('google.generativeai.GenerativeModel')
def test_product_manager_initialization(mock_model):
    """Test that ProductManager can be initialized with default model."""
    mock_model.return_value = MagicMock()
    mock_model.return_value.generate_content.return_value = MagicMock()
    pm = ProductManager()
    assert pm.model == "gemini-2.0-flash"
    assert hasattr(pm, 'client'), "ProductManager should have a client attribute"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
