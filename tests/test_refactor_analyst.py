import pytest
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
from ai_agents.refactor_analyst import RefactorAnalyst

# Sample test data
SAMPLE_CODE = """
class UserService:
    def __init__(self):
        self.db = Database()
        self.logger = Logger()
        self.cache = Cache()
    
    def get_user(self, user_id: str):
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached
        
        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        self.cache.set(f"user:{user_id}", user)
        self.logger.info(f"Retrieved user {user_id}")
        return user
"""

SAMPLE_ARCHITECTURE = {
    "components": {
        "UserService": {
            "dependencies": ["Database", "Logger", "Cache"],
            "responsibilities": ["User management", "Data access"]
        }
    },
    "patterns": {
        "repository": True,
        "caching": True,
        "logging": True
    }
}

SAMPLE_CODE_FILES = {
    "user_service.py": SAMPLE_CODE,
    "database.py": """
class Database:
    def query(self, sql: str):
        # Direct SQL query - potential SQL injection
        pass
""",
    "cache.py": """
class Cache:
    def get(self, key: str):
        pass
    
    def set(self, key: str, value: any):
        pass
""",
    "logger.py": """
class Logger:
    def info(self, message: str):
        print(message)
"""
}

SAMPLE_CODEBASE_STATS = {
    "files": 4,
    "lines": 150,
    "classes": 4,
    "functions": 8,
    "dependencies": ["sqlite3", "redis", "logging"],
    "test_coverage": 65.5
}

SAMPLE_METRICS = {
    "files": 10,
    "lines": 500,
    "classes": 10,
    "functions": 20,
    "dependencies": ["sqlite3", "redis", "logging"],
    "test_coverage": 80.0
}

class AsyncMockResponse:
    """Mock async Gemini API response."""
    def __init__(self, text):
        self.text = text
        self.candidates = [self]  # Gemini API expects candidates

    async def __call__(self, *args, **kwargs):
        return self

    def __await__(self):
        async def _async_result():
            return self
        return _async_result().__await__()

@pytest.fixture
def refactor_analyst():
    """Create a RefactorAnalyst instance for testing."""
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        return RefactorAnalyst()

@pytest.mark.asyncio
async def test_analyze_code_quality(refactor_analyst):
    """Test code quality analysis."""
    mock_response = AsyncMockResponse("""
Code Structure:
- High coupling between UserService and dependencies
- Direct SQL queries pose security risk
- Lack of dependency injection

Performance:
- Inefficient caching strategy
- No connection pooling
- Missing error handling

Maintainability:
- Hardcoded SQL queries
- Limited test coverage
- Inconsistent logging

Modern Practices:
- Consider using ORM
- Implement dependency injection
- Add type hints
""")
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        analysis = await refactor_analyst.analyze_code_quality(SAMPLE_CODE)
        
        assert isinstance(analysis, dict)
        assert all(key in analysis for key in ["code_structure", "performance", "maintainability", "modern_practices"])
        assert len(analysis["code_structure"]) > 0
        assert len(analysis["performance"]) > 0
        assert len(analysis["maintainability"]) > 0
        assert len(analysis["modern_practices"]) > 0

@pytest.mark.asyncio
async def test_analyze_dependencies(refactor_analyst):
    """Test dependency analysis."""
    mock_response = AsyncMockResponse("""
Component Coupling:
- High coupling between Service and Repository layers
- Direct database access in controllers
- Tight coupling with external services

Dependency Patterns:
- Circular dependency in user management
- Missing dependency injection
- Service locator anti-pattern

Architectural Alignment:
- Layer violations in data access
- Direct repository access from UI
- Missing interface abstractions

Optimization Opportunities:
- Consolidate service interfaces
- Implement repository pattern
- Extract common dependencies
""")
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        analysis = await refactor_analyst.analyze_dependencies({"test.py": SAMPLE_CODE})
        
        assert isinstance(analysis, dict)
        assert all(key in analysis for key in ["coupling", "patterns", "architecture", "optimization"])
        assert len(analysis["coupling"]) > 0
        assert len(analysis["patterns"]) > 0
        assert len(analysis["architecture"]) > 0
        assert len(analysis["optimization"]) > 0

@pytest.mark.asyncio
async def test_assess_refactor_impact(refactor_analyst):
    """Test refactoring impact assessment."""
    mock_response = AsyncMockResponse("""
Risk Level:
- High risk in authentication changes
- Medium risk in database access
- Low risk in UI updates

Dependencies:
- User service affected
- Cache system impacted
- API endpoints need updates

Testing Requirements:
- Full regression suite
- Performance benchmarks
- Security audit

Timeline:
- Estimated 2-3 sprints
- Phased rollout recommended
- Requires coordination
""")
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        impact = await refactor_analyst.assess_refactor_impact(
            [{"name": "Auth Refactor", "description": "Update auth system"}],
            SAMPLE_METRICS
        )
        
        assert isinstance(impact, dict)
        assert all(key in impact for key in ["risk_level", "dependencies", "testing", "timeline"])
        assert len(impact["risk_level"]) > 0
        assert len(impact["dependencies"]) > 0
        assert len(impact["testing"]) > 0
        assert len(impact["timeline"]) > 0

@pytest.mark.asyncio
async def test_generate_automated_refactorings(refactor_analyst):
    """Test automated refactoring generation."""
    mock_response = AsyncMockResponse("""
Refactoring 1: Implement Dependency Injection
Before:
```python
class UserService:
    def __init__(self):
        self.db = Database()
```

After:
```python
class UserService:
    def __init__(self, db: Database):
        self.db = db
```

Refactoring 2: Extract Interface
Before:
```python
class Database:
    def query(self):
        pass
```

After:
```python
from abc import ABC, abstractmethod

class IDatabase(ABC):
    @abstractmethod
    def query(self):
        pass
```
""")
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        code = "class UserService:\n    def __init__(self):\n        self.db = Database()"
        analysis = {
            "coupling": ["High coupling with Database"],
            "patterns": ["Missing dependency injection"]
        }
        
        refactorings = await refactor_analyst.generate_automated_refactorings(code, analysis)
        
        assert isinstance(refactorings, list)
        assert len(refactorings) > 0
        assert "before" in refactorings[0]
        assert "after" in refactorings[0]
        assert "description" in refactorings[0]

@pytest.mark.asyncio
async def test_update_cursor_rules(refactor_analyst):
    """Test cursor rules update generation."""
    mock_response = AsyncMockResponse("""
[
    {
        "name": "dependency_injection",
        "pattern": "class.*?\\s*def\\s*__init__\\s*\\(\\s*self\\s*\\)\\s*:",
        "message": "Consider using dependency injection for better testability",
        "severity": "warning"
    },
    {
        "name": "interface_abstraction",
        "pattern": "class\\s+\\w+\\s*:",
        "message": "Consider defining an interface for better abstraction",
        "severity": "info"
    }
]
""")
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        suggestions = [{
            "title": "Implement Dependency Injection",
            "description": "Replace direct instantiation with DI"
        }]
        
        rules = await refactor_analyst.update_cursor_rules(suggestions)
        
        assert isinstance(rules, str)
        assert "dependency_injection" in rules
        assert "pattern" in rules
        assert "message" in rules

def test_parse_dependency_analysis():
    """Test dependency analysis parsing."""
    raw_analysis = """
Component Coupling:
- High coupling between modules
- Direct database access
- Tight service dependencies

Dependency Patterns:
- Circular dependencies found
- Missing dependency injection
- Service locator usage

Architectural Alignment:
- Layer violations detected
- Direct repository access
- Missing abstractions

Optimization Opportunities:
- Consolidate interfaces
- Implement repository pattern
- Extract shared dependencies
"""
    analyst = RefactorAnalyst()
    result = analyst._parse_dependency_analysis(raw_analysis)
    
    assert isinstance(result, dict)
    assert all(key in result for key in ["coupling", "patterns", "architecture", "optimization"])
    assert len(result["coupling"]) == 3
    assert len(result["patterns"]) == 3
    assert len(result["architecture"]) == 3
    assert len(result["optimization"]) == 3
    assert "High coupling between modules" in result["coupling"]

def test_parse_impact_assessment():
    """Test impact assessment parsing."""
    analyst = RefactorAnalyst()
    raw_assessment = """
Suggestion 1:
Scope of Impact:
- UserService
- Database layer
Dependencies: All data access
Testing: Update service tests

Risk Assessment:
Complexity: High
Challenges: Service changes
Regressions: Possible data issues

Resource Requirements:
Development: 1 week
Testing: 3 days
Deployment: Staged rollout

Business Impact:
Performance: +20% throughput
Maintenance: Easier updates
Tech Debt: -30%
"""
    
    result = analyst._parse_impact_assessment(raw_assessment)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "scope" in result[0]
    assert "risk" in result[0]
    assert "resources" in result[0]
    assert "business_impact" in result[0]
    
    assert len(result[0]["scope"]["affected_components"]) > 0
    assert len(result[0]["risk"]["complexity"]) > 0
    assert len(result[0]["resources"]["development"]) > 0
    assert len(result[0]["business_impact"]["performance"]) > 0

def test_parse_automated_suggestions():
    """Test automated suggestions parsing."""
    analyst = RefactorAnalyst()
    raw_suggestions = """
Suggestion 1:
Code Changes:
File: user_service.py
Line: 2-4
Change: Implement dependency injection

Examples:
Before:
```python
def __init__(self):
    self.db = Database()
```

After:
```python
def __init__(self, db: Database):
    self.db = db
```

Explanation:
Reduces coupling and improves testability.

Testing:
- Update constructor tests
- Add DI container tests
Validation: Verify initialization
"""
    
    result = analyst._parse_automated_suggestions(raw_suggestions)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "changes" in result[0]
    assert "examples" in result[0]
    assert "explanation" in result[0]
    assert "testing" in result[0]
    
    assert len(result[0]["changes"]) > 0
    assert "before" in result[0]["examples"]
    assert "after" in result[0]["examples"]
    assert len(result[0]["testing"]["updates"]) > 0
