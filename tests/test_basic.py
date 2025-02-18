"""Basic tests for the AI Agents framework."""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import ai_agents.base_agent as base_agent

def test_base_agent_init():
    """Test basic initialization of BaseAgent."""
    agent = base_agent.BaseAgent()
    assert agent.model == "gemini-2.0-flash"
