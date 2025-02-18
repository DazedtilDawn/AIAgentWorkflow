"""AI Agents Package

This package contains the implementation of specialized AI agents for the automated
software development pipeline using Gemini 2.0 Flash.
"""

# Core agent classes
from .base_agent import BaseAgent
from .product_manager import ProductManager
from .brainstorm_facilitator import BrainstormFacilitator
from .architect import Architect
from .planner import Planner
from .engineer import Engineer
from .reviewer import Reviewer
from .qa_engineer import QAEngineer
from .devops_manager import DevOpsManager
from .monitoring_analytics import MonitoringAnalytics
from .refactor_analyst import RefactorAnalyst
from .documenter import Documenter
from .project_manager import ProjectManager

__version__ = "3.2.0"
