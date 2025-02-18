import pytest
import os
from pathlib import Path
import json
import yaml
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

# Import all agent classes
from ai_agents.product_manager import ProductManager
from ai_agents.brainstorm_facilitator import BrainstormFacilitator
from ai_agents.architect import Architect
from ai_agents.planner import Planner
from ai_agents.engineer import Engineer
from ai_agents.reviewer import Reviewer
from ai_agents.qa_engineer import QAEngineer
from ai_agents.devops_manager import DevOpsManager
from ai_agents.monitoring_analytics import MonitoringAnalytics
from ai_agents.refactor_analyst import RefactorAnalyst
from ai_agents.documenter import Documenter
from ai_agents.project_manager import ProjectManager

# Test data
SAMPLE_USER_PROMPT = """
Create a modern web application for task management with the following features:
1. User authentication
2. Task creation and management
3. Team collaboration
4. Real-time updates
5. Performance analytics
"""

@pytest.fixture
def test_dir():
    """Create and return a test directory."""
    test_dir = Path(__file__).parent / "test_artifacts"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture
def mock_responses():
    """Create mock responses for different test cases."""
    return {
        'market_context': {
            "target_market": ["Small to medium businesses", "Remote teams"],
            "competitors": [
                {"name": "Trello", "strengths": ["Ease of use", "Visual boards"]},
                {"name": "Asana", "strengths": ["Team collaboration", "Task tracking"]}
            ],
            "market_trends": [
                "Remote work adoption",
                "Real-time collaboration",
                "Mobile-first design"
            ],
            "user_demographics": {
                "age_range": "25-45",
                "roles": ["Project managers", "Team leads", "Contributors"],
                "tech_proficiency": "Medium to high"
            },
            "pain_points": [
                "Task tracking across teams",
                "Real-time status updates",
                "Performance monitoring"
            ],
            "opportunities": [
                "AI-powered task automation",
                "Advanced analytics",
                "Integration capabilities"
            ]
        },
        'user_personas': [
            {
                "name": "Sarah",
                "role": "Project Manager",
                "goals": ["Efficient task tracking", "Team coordination"],
                "challenges": ["Multiple project tracking", "Resource allocation"],
                "preferences": {
                    "communication": "Real-time",
                    "tools": "Web-based",
                    "workflow": "Agile"
                },
                "technical_proficiency": "High"
            },
            {
                "name": "Mike",
                "role": "Team Lead",
                "goals": ["Sprint planning", "Team productivity"],
                "challenges": ["Task dependencies", "Progress tracking"],
                "preferences": {
                    "communication": "Async",
                    "tools": "CLI",
                    "workflow": "Kanban"
                },
                "technical_proficiency": "Medium"
            }
        ],
        'feature_specs': [
            {
                "name": "Task Management",
                "description": "Core task tracking functionality",
                "priority": "High",
                "user_stories": [
                    "As a PM, I can create tasks",
                    "As a user, I can view my tasks"
                ],
                "acceptance_criteria": [
                    "Create tasks with title and description",
                    "Assign tasks to team members"
                ],
                "technical_requirements": [
                    "RESTful API",
                    "Real-time updates"
                ],
                "dependencies": ["User Authentication"],
                "estimated_effort": "Medium",
                "risks": [
                    "Data consistency in real-time updates",
                    "Performance at scale"
                ]
            }
        ],
        'product_spec': {
            "title": "Task Management System",
            "description": "Modern web application for collaborative task management",
            "version": datetime.now().strftime("%Y.%m.%d"),
            "scope": {
                "in_scope": ["Task management", "Team collaboration"],
                "out_of_scope": ["Billing", "Time tracking"]
            },
            "audience": [
                {
                    "name": "Sarah",
                    "role": "Project Manager",
                    "goals": ["Efficient task tracking"],
                    "challenges": ["Multiple project tracking"],
                    "preferences": {"workflow": "Agile"},
                    "technical_proficiency": "High"
                }
            ],
            "market_context": {
                "target_market": ["Small to medium businesses"],
                "competitors": [{"name": "Trello", "strengths": ["Ease of use"]}],
                "market_trends": ["Remote work adoption"],
                "user_demographics": {"roles": ["Project managers"]},
                "pain_points": ["Task tracking"],
                "opportunities": ["AI automation"]
            },
            "features": [
                {
                    "name": "Task Management",
                    "description": "Core functionality",
                    "priority": "High",
                    "user_stories": ["Create tasks"],
                    "acceptance_criteria": ["CRUD operations"],
                    "technical_requirements": ["API"],
                    "dependencies": ["Auth"],
                    "estimated_effort": "Medium",
                    "risks": ["Performance"]
                }
            ],
            "success_metrics": {
                "adoption": ["80% team engagement"],
                "performance": ["99.9% uptime"]
            },
            "technical_requirements": [
                "Cloud infrastructure",
                "Microservices architecture"
            ],
            "constraints": [
                "Budget limitations",
                "Timeline constraints"
            ],
            "timeline": {
                "phases": ["Planning", "Development"],
                "milestones": ["MVP", "Beta"]
            },
            "dependencies": {
                "external": ["Cloud provider"],
                "internal": ["DevOps team"]
            },
            "risks_and_mitigations": {
                "technical": ["Scalability issues"],
                "business": ["Market competition"]
            },
            "assumptions": [
                "Stable internet connectivity",
                "Modern browser support"
            ]
        }
    }

@pytest.fixture
def mock_gemini(mock_responses):
    """Create a mock Gemini client."""
    mock_client = AsyncMock()
    
    async def mock_generate_content(*args, **kwargs):
        mock_response = MagicMock()
        # Determine which response to return based on the prompt
        prompt = args[0] if args else kwargs.get('prompt', '')
        
        if 'market context' in prompt.lower():
            mock_response.text = json.dumps(mock_responses['market_context'])
        elif 'user persona' in prompt.lower():
            # Return a list of user personas
            mock_response.text = json.dumps([{
                "name": "Sarah",
                "role": "Project Manager",
                "goals": ["Efficient task tracking", "Team coordination"],
                "challenges": ["Multiple project tracking", "Resource allocation"],
                "preferences": {
                    "communication": "Real-time",
                    "tools": "Web-based",
                    "workflow": "Agile"
                },
                "technical_proficiency": "High"
            }, {
                "name": "Mike",
                "role": "Team Lead",
                "goals": ["Sprint planning", "Team productivity"],
                "challenges": ["Task dependencies", "Progress tracking"],
                "preferences": {
                    "communication": "Async",
                    "tools": "CLI",
                    "workflow": "Kanban"
                },
                "technical_proficiency": "Medium"
            }])
        elif 'feature' in prompt.lower():
            # Return a list of feature specifications
            mock_response.text = json.dumps([{
                "name": "Task Management",
                "description": "Core task tracking functionality",
                "priority": "High",
                "user_stories": [
                    "As a PM, I can create tasks",
                    "As a user, I can view my tasks"
                ],
                "acceptance_criteria": [
                    "Create tasks with title and description",
                    "Assign tasks to team members"
                ],
                "technical_requirements": [
                    "RESTful API",
                    "Real-time updates"
                ],
                "dependencies": ["User Authentication"],
                "estimated_effort": "Medium",
                "risks": [
                    "Data consistency in real-time updates",
                    "Performance at scale"
                ]
            }])
        elif 'product spec' in prompt.lower() or 'specification' in prompt.lower():
            # Return a complete product specification
            mock_response.text = json.dumps({
                "title": "Task Management System",
                "description": "Modern web application for collaborative task management",
                "version": datetime.now().strftime("%Y.%m.%d"),
                "scope": {
                    "in_scope": ["Task management", "Team collaboration"],
                    "out_of_scope": ["Billing", "Time tracking"]
                },
                "audience": [{
                    "name": "Sarah",
                    "role": "Project Manager",
                    "goals": ["Efficient task tracking"],
                    "challenges": ["Multiple project tracking"],
                    "preferences": {"workflow": "Agile"},
                    "technical_proficiency": "High"
                }],
                "market_context": {
                    "target_market": ["Small to medium businesses"],
                    "competitors": [{"name": "Trello", "strengths": ["Ease of use"]}],
                    "market_trends": ["Remote work adoption"],
                    "user_demographics": {"roles": ["Project managers"]},
                    "pain_points": ["Task tracking"],
                    "opportunities": ["AI automation"]
                },
                "features": [{
                    "name": "Task Management",
                    "description": "Core functionality",
                    "priority": "High",
                    "user_stories": ["Create tasks"],
                    "acceptance_criteria": ["CRUD operations"],
                    "technical_requirements": ["API"],
                    "dependencies": ["Auth"],
                    "estimated_effort": "Medium",
                    "risks": ["Performance"]
                }],
                "success_metrics": {
                    "adoption": ["80% team engagement"],
                    "performance": ["99.9% uptime"]
                },
                "technical_requirements": [
                    "Cloud infrastructure",
                    "Microservices architecture"
                ],
                "constraints": [
                    "Budget limitations",
                    "Timeline constraints"
                ],
                "timeline": {
                    "phases": ["Planning", "Development"],
                    "milestones": ["MVP", "Beta"]
                },
                "dependencies": {
                    "external": ["Cloud provider"],
                    "internal": ["DevOps team"]
                },
                "risks_and_mitigations": {
                    "technical": ["Scalability issues"],
                    "business": ["Market competition"]
                },
                "assumptions": [
                    "Stable internet connectivity",
                    "Modern browser support"
                ]
            })
        else:
            # Default response for other cases
            mock_response.text = json.dumps({
                "status": "success",
                "message": "Mock response for: " + prompt[:50],
                "data": mock_responses['product_spec']
            })
        return mock_response
    
    mock_client.generate_content = mock_generate_content
    
    with patch('google.generativeai.GenerativeModel', return_value=mock_client):
        yield mock_client

@pytest.fixture
def agents(test_dir, mock_gemini):
    """Initialize all agents with test configuration."""
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        return {
            'product_manager': ProductManager(),
            'brainstorm_facilitator': BrainstormFacilitator(),
            'architect': Architect(),
            'planner': Planner(),
            'engineer': Engineer(),
            'reviewer': Reviewer(),
            'qa_engineer': QAEngineer(),
            'devops_manager': DevOpsManager(),
            'monitoring_analytics': MonitoringAnalytics(),
            'refactor_analyst': RefactorAnalyst(),
            'documenter': Documenter(),
            'project_manager': ProjectManager()
        }

@pytest.mark.asyncio
async def test_end_to_end_workflow(test_dir, agents, mock_gemini, mock_responses):
    """Test the complete development workflow from ideation to deployment."""
    try:
        # Step 1: Product Manager creates specifications
        specs = await agents['product_manager'].generate_specifications(SAMPLE_USER_PROMPT)
        specs_file = test_dir / "PRODUCT_SPECS.md"
        specs_file.write_text(specs)
        
        # Step 2: Brainstorm Facilitator generates ideas
        brainstorm = await agents['brainstorm_facilitator'].generate_ideas(
            specs,
            num_ideas=3
        )
        brainstorm_file = test_dir / "BRAINSTORM_OUTCOME.md"
        brainstorm_file.write_text(brainstorm)
        
        # Step 3: Architect designs system
        architecture = await agents['architect'].design_system(
            specs,
            brainstorm
        )
        arch_file = test_dir / "SYSTEM_ARCHITECTURE.md"
        arch_file.write_text(architecture)
        
        # Step 4: Planner creates development plan
        plan = await agents['planner'].create_plan(
            specs,
            architecture
        )
        plan_file = test_dir / "PLAN.md"
        plan_file.write_text(plan)
        
        # Step 5: Engineer implements features
        implementation = await agents['engineer'].implement_features(
            specs,
            plan
        )
        
        # Step 6: Reviewer checks code
        review = await agents['reviewer'].review_code(
            implementation,
            specs
        )
        review_file = test_dir / "REVIEW.md"
        review_file.write_text(review)
        
        # Step 7: QA Engineer tests
        test_results = await agents['qa_engineer'].run_tests(
            implementation,
            specs
        )
        test_file = test_dir / "TEST_DEBUG_REPORT.md"
        test_file.write_text(test_results)
        
        # Step 8: DevOps Manager deploys
        deployment = await agents['devops_manager'].deploy_system(
            implementation,
            test_results
        )
        deploy_file = test_dir / "DEPLOYMENT_LOG.md"
        deploy_file.write_text(deployment)
        
        # Step 9: Monitoring & Analytics generates report
        monitoring = await agents['monitoring_analytics'].generate_report(
            deployment,
            test_results
        )
        monitoring_file = test_dir / "MONITORING_REPORT.md"
        monitoring_file.write_text(monitoring)
        
        # Step 10: Refactor Analyst suggests improvements
        refactor = await agents['refactor_analyst'].analyze_code(
            implementation,
            monitoring
        )
        refactor_file = test_dir / "REFACTOR_SUGGESTIONS.md"
        refactor_file.write_text(refactor)
        
        # Step 11: Documenter consolidates documentation
        docs = await agents['documenter'].generate_documentation(
            [
                specs_file,
                brainstorm_file,
                arch_file,
                plan_file,
                review_file,
                test_file,
                deploy_file,
                monitoring_file,
                refactor_file
            ]
        )
        docs_file = test_dir / "DOCUMENTATION.md"
        docs_file.write_text(docs)
        
        # Step 12: Project Manager coordinates
        progress = await agents['project_manager'].validate_cross_role_outputs(
            {
                'product_manager': specs,
                'brainstorm_facilitator': brainstorm,
                'architect': architecture,
                'planner': plan,
                'engineer': implementation,
                'reviewer': review,
                'qa_engineer': test_results,
                'devops_manager': deployment,
                'monitoring_analytics': monitoring,
                'refactor_analyst': refactor,
                'documenter': docs
            }
        )
        progress_file = test_dir / "PROJECT_STATUS.md"
        progress_file.write_text(progress)
        
        # Verify all files were created
        assert specs_file.exists()
        assert brainstorm_file.exists()
        assert arch_file.exists()
        assert plan_file.exists()
        assert review_file.exists()
        assert test_file.exists()
        assert deploy_file.exists()
        assert monitoring_file.exists()
        assert refactor_file.exists()
        assert docs_file.exists()
        assert progress_file.exists()
        
    except Exception as e:
        pytest.fail(f"End-to-end test failed: {str(e)}")

@pytest.mark.asyncio
async def test_cross_role_validation(test_dir, agents, mock_gemini, mock_responses):
    """Test validation and consensus between different roles."""
    try:
        # Test Product Manager and Architect alignment
        specs = await agents['product_manager'].generate_specifications(SAMPLE_USER_PROMPT)
        architecture = await agents['architect'].design_system(
            specs,
            specs
        )
        
        # Test Engineer and QA alignment
        implementation = await agents['engineer'].implement_features(
            specs,
            architecture
        )
        test_results = await agents['qa_engineer'].run_tests(
            implementation,
            specs
        )
        
        # Test DevOps and Monitoring alignment
        deployment = await agents['devops_manager'].deploy_system(
            implementation,
            test_results
        )
        monitoring = await agents['monitoring_analytics'].generate_report(
            deployment,
            test_results
        )
        
        # Verify cross-role validation
        validation = await agents['project_manager'].validate_cross_role_outputs({
            'product_manager': specs,
            'architect': architecture,
            'engineer': implementation,
            'qa_engineer': test_results,
            'devops_manager': deployment,
            'monitoring_analytics': monitoring
        })
        
        validation_file = test_dir / "VALIDATION_REPORT.md"
        validation_file.write_text(validation)
        assert validation_file.exists()
        
    except Exception as e:
        pytest.fail(f"Cross-role validation test failed: {str(e)}")

@pytest.mark.asyncio
async def test_feedback_loops(test_dir, agents, mock_gemini, mock_responses):
    """Test continuous feedback and improvement loops."""
    try:
        # Initial deployment
        implementation = await agents['engineer'].implement_features(
            mock_responses['product_spec'],
            mock_responses['product_spec']
        )
        test_results = await agents['qa_engineer'].run_tests(
            implementation,
            mock_responses['product_spec']
        )
        deployment = await agents['devops_manager'].deploy_system(
            implementation,
            test_results
        )
        
        # Generate monitoring report
        monitoring = await agents['monitoring_analytics'].generate_report(
            deployment,
            test_results
        )
        
        # Analyze for improvements
        refactor = await agents['refactor_analyst'].analyze_code(
            implementation,
            monitoring
        )
        
        # Implement improvements
        improved_implementation = await agents['engineer'].implement_features(
            mock_responses['product_spec'],
            refactor
        )
        
        # Verify improvements
        improved_test_results = await agents['qa_engineer'].run_tests(
            improved_implementation,
            mock_responses['product_spec']
        )
        
        # Save feedback loop artifacts
        feedback_dir = test_dir / "feedback_loop"
        feedback_dir.mkdir(exist_ok=True)
        
        (feedback_dir / "initial_deployment.md").write_text(deployment)
        (feedback_dir / "monitoring_report.md").write_text(monitoring)
        (feedback_dir / "refactor_suggestions.md").write_text(refactor)
        (feedback_dir / "improved_implementation.md").write_text(improved_implementation)
        (feedback_dir / "improved_test_results.md").write_text(improved_test_results)
        
        assert (feedback_dir / "initial_deployment.md").exists()
        assert (feedback_dir / "monitoring_report.md").exists()
        assert (feedback_dir / "refactor_suggestions.md").exists()
        assert (feedback_dir / "improved_implementation.md").exists()
        assert (feedback_dir / "improved_test_results.md").exists()
        
    except Exception as e:
        pytest.fail(f"Feedback loops test failed: {str(e)}")

@pytest.mark.asyncio
async def test_error_handling(test_dir, agents, mock_gemini, mock_responses):
    """Test system resilience and error handling."""
    try:
        # Test invalid input handling
        with pytest.raises(Exception):
            await agents['product_manager'].generate_specifications("")
        
        # Test missing dependency handling
        with pytest.raises(Exception):
            await agents['engineer'].implement_features(
                mock_responses['product_spec'],
                ""
            )
        
        # Test validation failure handling
        with pytest.raises(Exception):
            await agents['qa_engineer'].run_tests(
                "",
                mock_responses['product_spec']
            )
        
        # Test deployment error handling
        with pytest.raises(Exception):
            await agents['devops_manager'].deploy_system(
                "",
                ""
            )
        
    except Exception as e:
        pytest.fail(f"Error handling test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
