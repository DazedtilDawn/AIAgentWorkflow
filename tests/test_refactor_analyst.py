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

@pytest.fixture
def refactor_analyst():
    """Create a RefactorAnalyst instance for testing."""
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        return RefactorAnalyst()

@pytest.mark.asyncio
async def test_analyze_code_quality(refactor_analyst):
    """Test code quality analysis."""
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = """
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
"""
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        analysis = await refactor_analyst.analyze_code_quality(SAMPLE_CODE)
        
        assert isinstance(analysis, dict)
        assert "code_structure" in analysis
        assert "performance" in analysis
        assert "maintainability" in analysis
        assert "modern_practices" in analysis

@pytest.mark.asyncio
async def test_analyze_dependencies(refactor_analyst):
    """Test dependency analysis."""
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = """
Component Coupling:
- UserService has tight coupling with Database
- Direct dependency on concrete implementations
Recommendation: Use dependency injection

Dependency Patterns:
- Circular dependency risk between Cache and Database
- Missing repository pattern
Improvement: Implement repository pattern

Architectural Alignment:
- Database access in service layer
- Missing clear boundaries
Solution: Introduce repository layer

Optimization Opportunities:
- Shared caching logic
- Duplicate logging setup
Suggestion: Create shared infrastructure layer
"""
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        analysis = await refactor_analyst.analyze_dependencies(
            SAMPLE_CODE_FILES, SAMPLE_ARCHITECTURE
        )
        
        assert isinstance(analysis, dict)
        assert "component_coupling" in analysis
        assert "dependency_patterns" in analysis
        assert "architectural_alignment" in analysis
        assert "optimization_opportunities" in analysis

@pytest.mark.asyncio
async def test_assess_refactor_impact(refactor_analyst):
    """Test refactoring impact assessment."""
    suggestions = [{
        "title": "Implement Dependency Injection",
        "description": "Replace direct instantiation with DI container"
    }]
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = """
Suggestion 1:
Scope of Impact:
- Affected components: UserService, Database, Cache, Logger
Dependencies: All service classes
Testing: Update all service tests

Risk Assessment:
Complexity: Medium
Challenges: Service initialization changes
Regressions: Potential service startup issues

Resource Requirements:
Development: 3-5 days
Testing: 2-3 days
Deployment: Requires careful staging

Business Impact:
Performance: Minimal immediate impact
Maintenance: Significant improvement
Tech Debt: Major reduction
"""
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        assessment = await refactor_analyst.assess_refactor_impact(
            suggestions, SAMPLE_CODEBASE_STATS
        )
        
        assert isinstance(assessment, list)
        assert len(assessment) > 0
        assert "scope" in assessment[0]
        assert "risk" in assessment[0]
        assert "resources" in assessment[0]
        assert "business_impact" in assessment[0]

@pytest.mark.asyncio
async def test_generate_automated_refactorings(refactor_analyst):
    """Test automated refactoring suggestion generation."""
    analysis = {
        "code_structure": ["High coupling", "Direct SQL queries"],
        "performance": ["Inefficient caching"],
        "maintainability": ["Limited test coverage"]
    }
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = """
Suggestion 1:
Code Changes:
File: user_service.py
Line: 2-4
Change: Replace direct instantiation with dependency injection

Examples:
Before:
```python
def __init__(self):
    self.db = Database()
    self.logger = Logger()
    self.cache = Cache()
```

After:
```python
def __init__(self, db: Database, logger: Logger, cache: Cache):
    self.db = db
    self.logger = logger
    self.cache = cache
```

Explanation:
Implements dependency injection to reduce coupling and improve testability.

Testing:
- Update UserService constructor tests
- Add integration tests for DI container
Validation: Verify all services initialize correctly
"""
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        suggestions = await refactor_analyst.generate_automated_refactorings(
            SAMPLE_CODE, analysis
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "changes" in suggestions[0]
        assert "examples" in suggestions[0]
        assert "explanation" in suggestions[0]
        assert "testing" in suggestions[0]

@pytest.mark.asyncio
async def test_update_cursor_rules(refactor_analyst):
    """Test cursor rules update."""
    suggestions = [{
        "category": "code_structure",
        "changes": [{
            "file": "user_service.py",
            "change": "Implement dependency injection"
        }]
    }]
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = """
{
    "rules": {
        "dependency_injection": {
            "pattern": "new (?:Database|Logger|Cache)\\(\\)",
            "message": "Use dependency injection instead of direct instantiation",
            "severity": "warning"
        },
        "sql_injection": {
            "pattern": "SELECT.*\\{.*\\}",
            "message": "Potential SQL injection risk",
            "severity": "error"
        }
    }
}
"""
    
    with patch('google.generativeai.GenerativeModel.generate_content', 
               return_value=mock_response):
        rules = await refactor_analyst.update_cursor_rules(suggestions)
        
        assert isinstance(rules, str)
        assert "dependency_injection" in rules
        assert "sql_injection" in rules

def test_parse_dependency_analysis():
    """Test dependency analysis parsing."""
    analyst = RefactorAnalyst()
    raw_analysis = """
Component Coupling:
- High coupling with Database
- Direct instantiation
Recommendation: Use dependency injection

Dependency Patterns:
- Circular dependencies
- Missing abstractions
Improvement: Add interfaces

Architectural Alignment:
- Layer violations
- Mixed concerns
Solution: Separate layers

Optimization Opportunities:
- Shared caching
- Duplicate logging
Suggestion: Create shared services
"""
    
    result = analyst._parse_dependency_analysis(raw_analysis)
    
    assert isinstance(result, dict)
    assert "component_coupling" in result
    assert "dependency_patterns" in result
    assert "architectural_alignment" in result
    assert "optimization_opportunities" in result
    
    assert len(result["component_coupling"]["issues"]) > 0
    assert len(result["dependency_patterns"]["improvements"]) > 0
    assert len(result["architectural_alignment"]["solutions"]) > 0
    assert len(result["optimization_opportunities"]["suggestions"]) > 0

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
