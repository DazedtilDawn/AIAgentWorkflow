import click
import os
from datetime import datetime
from loguru import logger
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import re
from dataclasses import dataclass
import yaml
from .base_agent import BaseAgent

@dataclass
class RiskAssessment:
    category: str
    severity: str
    probability: float
    impact: str
    mitigation_steps: List[str]
    contingency_plan: str
    owner: str

@dataclass
class WorkflowStage:
    name: str
    status: str
    roles: List[str]
    dependencies: List[str]
    artifacts: List[str]
    validation_rules: List[str]
    completion_criteria: List[str]

@dataclass
class TeamSyncUpdate:
    timestamp: datetime
    role: str
    status: str
    progress: float
    blockers: List[str]
    needs: List[str]
    next_steps: List[str]
    dependencies: List[str]

class ProjectManager(BaseAgent):
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Project Manager with AI configuration."""
        super().__init__(model)
        
        # Initialize project directory
        self.project_dir = Path(__file__).parent.parent
        self.artifacts_dir = self.project_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

    async def validate_cross_role_outputs(self, 
                                       role_outputs: Dict[str, str],
                                       validation_rules: Optional[Dict] = None) -> Dict:
        """Validate outputs from different roles for consistency."""
        system_message = """You are a Project Manager specializing in ensuring 
        consistency and quality across multi-agent development processes."""
        
        context = "## Role Outputs\n"
        for role, output in role_outputs.items():
            context += f"\n### {role}\n{output}\n"
        
        if validation_rules:
            context += "\n## Validation Rules\n"
            for rule_type, rules in validation_rules.items():
                context += f"\n### {rule_type}\n"
                for rule in rules:
                    context += f"- {rule}\n"
        
        prompt = f"""Based on the following role outputs and validation rules:

        {context}

        Validate the consistency and quality across roles:
        1. Requirements Traceability
           - Product specs to architecture
           - Architecture to implementation
           - Implementation to tests
        2. Cross-Role Alignment
           - Technical decisions
           - Design patterns
           - Naming conventions
        3. Quality Standards
           - Code quality
           - Documentation
           - Test coverage
        4. Process Compliance
           - Development workflow
           - Review process
           - Deployment procedures
        """
        
        try:
            validation = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_validation(validation)
        except Exception as e:
            logger.error(f"Error validating cross-role outputs: {str(e)}")
            raise
    
    async def generate_consensus_resolution(self, 
                                         conflicts: List[Dict],
                                         context: Optional[Dict] = None) -> Dict:
        """Generate resolution for conflicts between roles."""
        system_message = """You are a Consensus Builder specializing in resolving 
        conflicts and aligning different perspectives in development processes."""
        
        conflict_context = "## Conflicts\n"
        for conflict in conflicts:
            conflict_context += f"\n### {conflict.get('title')}\n"
            conflict_context += f"Roles: {', '.join(conflict.get('roles', []))}\n"
            conflict_context += f"Description: {conflict.get('description')}\n"
            conflict_context += f"Impact: {conflict.get('impact')}\n"
        
        if context:
            conflict_context += "\n## Project Context\n"
            for key, value in context.items():
                conflict_context += f"\n### {key}\n{value}\n"
        
        prompt = f"""Based on the following conflicts and context:

        {conflict_context}

        Generate consensus resolutions that:
        1. Address all stakeholder concerns
        2. Maintain project quality
        3. Consider technical constraints
        4. Align with project goals
        5. Minimize disruption
        6. Enable forward progress
        
        For each conflict provide:
        1. Resolution approach
        2. Implementation steps
        3. Impact assessment
        4. Risk mitigation
        5. Communication plan
        """
        
        try:
            resolution = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_resolution(resolution)
        except Exception as e:
            logger.error(f"Error generating consensus resolution: {str(e)}")
            raise
    
    async def generate_progress_report(self, 
                                    role_statuses: Dict[str, Dict],
                                    metrics: Optional[Dict] = None) -> str:
        """Generate comprehensive progress report."""
        system_message = """You are a Project Status Analyst specializing in 
        creating clear, actionable progress reports for development projects."""
        
        context = "## Role Statuses\n"
        for role, status in role_statuses.items():
            context += f"\n### {role}\n"
            context += f"Status: {status.get('status')}\n"
            context += f"Progress: {status.get('progress')}%\n"
            context += f"Blockers: {', '.join(status.get('blockers', []))}\n"
            context += f"Next Steps: {status.get('next_steps')}\n"
        
        if metrics:
            context += "\n## Project Metrics\n"
            for metric_type, value in metrics.items():
                context += f"- {metric_type}: {value}\n"
        
        prompt = f"""Based on the following status information:

        {context}

        Generate a progress report that covers:
        1. Overall Project Status
           - Progress summary
           - Key achievements
           - Current challenges
        2. Role-specific Updates
           - Completed tasks
           - Ongoing work
           - Blockers and risks
        3. Quality Metrics
           - Code quality
           - Test coverage
           - Documentation status
        4. Next Steps
           - Immediate actions
           - Medium-term goals
           - Risk mitigation
        5. Recommendations
           - Process improvements
           - Resource allocation
           - Technical decisions
        """
        
        try:
            report = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._format_progress_report(report)
        except Exception as e:
            logger.error(f"Error generating progress report: {str(e)}")
            raise
    
    async def orchestrate_workflow(self,
                                stages: List[WorkflowStage],
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """Orchestrate the multi-agent workflow and manage stage transitions."""
        system_message = """You are a Workflow Orchestrator specializing in managing
        complex multi-agent development processes."""
        
        stages_context = "## Workflow Stages\n"
        for stage in stages:
            stages_context += f"""
            ### {stage.name}
            Status: {stage.status}
            Roles: {', '.join(stage.roles)}
            Dependencies: {', '.join(stage.dependencies)}
            Artifacts: {', '.join(stage.artifacts)}
            Validation Rules: {', '.join(stage.validation_rules)}
            Completion Criteria: {', '.join(stage.completion_criteria)}
            """
        
        if context:
            stages_context += "\n## Project Context\n"
            for key, value in context.items():
                stages_context += f"\n### {key}\n{value}\n"
        
        prompt = f"""Based on the workflow stages and context:

        {stages_context}

        Analyze and orchestrate the workflow:
        1. Stage Dependencies
           - Validate prerequisites
           - Check artifact availability
           - Verify role readiness
        
        2. Parallel Execution
           - Identify parallel opportunities
           - Manage resource conflicts
           - Coordinate handoffs
        
        3. Quality Gates
           - Validate completion criteria
           - Check cross-role alignment
           - Verify artifacts
        
        4. Risk Management
           - Identify bottlenecks
           - Flag potential issues
           - Suggest mitigations
        
        Provide orchestration decisions for:
        1. Stage transitions
        2. Role assignments
        3. Resource allocation
        4. Quality checkpoints
        5. Risk mitigations
        """
        
        try:
            orchestration = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_orchestration(orchestration)
        except Exception as e:
            logger.error(f"Error orchestrating workflow: {str(e)}")
            raise

    async def assess_project_risks(self,
                                role_statuses: Dict[str, Dict],
                                metrics: Optional[Dict] = None) -> List[RiskAssessment]:
        """Assess project risks and generate mitigation strategies."""
        system_message = """You are a Risk Management Expert specializing in identifying
        and mitigating risks in complex development projects."""
        
        status_context = "## Role Statuses\n"
        for role, status in role_statuses.items():
            status_context += f"""
            ### {role}
            Status: {status.get('status')}
            Progress: {status.get('progress')}%
            Blockers: {', '.join(status.get('blockers', []))}
            Dependencies: {', '.join(status.get('dependencies', []))}
            """
        
        if metrics:
            status_context += "\n## Project Metrics\n"
            for metric, value in metrics.items():
                status_context += f"{metric}: {value}\n"
        
        prompt = f"""Based on the current project status:

        {status_context}

        Assess project risks focusing on:
        1. Technical Risks
           - Architecture decisions
           - Technology choices
           - Integration points
        
        2. Process Risks
           - Role dependencies
           - Workflow bottlenecks
           - Quality gates
        
        3. Resource Risks
           - Role availability
           - Skill requirements
           - Tool dependencies
        
        4. Quality Risks
           - Testing coverage
           - Documentation
           - Technical debt
        
        For each risk provide:
        1. Risk category and severity
        2. Probability and impact
        3. Mitigation steps
        4. Contingency plans
        5. Risk owner
        """
        
        try:
            assessment = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_risk_assessment(assessment)
        except Exception as e:
            logger.error(f"Error assessing project risks: {str(e)}")
            raise

    async def coordinate_team_sync(self,
                                updates: List[TeamSyncUpdate],
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """Coordinate team synchronization and resolve dependencies."""
        system_message = """You are a Team Coordination Expert specializing in
        facilitating effective collaboration in multi-agent development teams."""
        
        updates_context = "## Team Updates\n"
        for update in updates:
            updates_context += f"""
            ### {update.role} ({update.timestamp})
            Status: {update.status}
            Progress: {update.progress}%
            Blockers: {', '.join(update.blockers)}
            Needs: {', '.join(update.needs)}
            Next Steps: {', '.join(update.next_steps)}
            Dependencies: {', '.join(update.dependencies)}
            """
        
        if context:
            updates_context += "\n## Project Context\n"
            for key, value in context.items():
                updates_context += f"\n### {key}\n{value}\n"
        
        prompt = f"""Based on the team updates and context:

        {updates_context}

        Coordinate team activities focusing on:
        1. Dependency Resolution
           - Identify blocking issues
           - Prioritize dependencies
           - Suggest workarounds
        
        2. Resource Allocation
           - Balance workload
           - Optimize parallel work
           - Address bottlenecks
        
        3. Communication Needs
           - Flag critical updates
           - Identify sync points
           - Suggest collaborations
        
        4. Progress Alignment
           - Track dependencies
           - Verify progress
           - Identify gaps
        
        Provide coordination decisions for:
        1. Immediate actions
        2. Resource adjustments
        3. Communication needs
        4. Timeline impacts
        """
        
        try:
            coordination = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_coordination(coordination)
        except Exception as e:
            logger.error(f"Error coordinating team sync: {str(e)}")
            raise

    def _parse_validation(self, raw_validation: str) -> Dict:
        """Parse the raw validation results into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_validation}  # Simplified for example
    
    def _parse_resolution(self, raw_resolution: str) -> Dict:
        """Parse the raw resolution into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_resolution}  # Simplified for example
    
    def _format_progress_report(self, raw_report: str) -> str:
        """Format the raw progress report into a structured document."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# Project Progress Report
Generated: {timestamp}

"""
        return header + raw_report

    def _parse_orchestration(self, raw_orchestration: str) -> Dict[str, Any]:
        """Parse workflow orchestration decisions into structured format."""
        try:
            # Extract sections using regex
            transitions = re.findall(r"Stage Transitions:(.*?)(?=\n\n|$)", 
                                  raw_orchestration, re.DOTALL)
            assignments = re.findall(r"Role Assignments:(.*?)(?=\n\n|$)", 
                                  raw_orchestration, re.DOTALL)
            resources = re.findall(r"Resource Allocation:(.*?)(?=\n\n|$)", 
                                raw_orchestration, re.DOTALL)
            checkpoints = re.findall(r"Quality Checkpoints:(.*?)(?=\n\n|$)", 
                                  raw_orchestration, re.DOTALL)
            
            return {
                "stage_transitions": self._extract_items(transitions[0] if transitions else "", 
                                                      r"- (.*?)(?=\n|$)"),
                "role_assignments": self._extract_items(assignments[0] if assignments else "", 
                                                    r"- (.*?)(?=\n|$)"),
                "resource_allocation": self._extract_items(resources[0] if resources else "", 
                                                       r"- (.*?)(?=\n|$)"),
                "quality_checkpoints": self._extract_items(checkpoints[0] if checkpoints else "", 
                                                       r"- (.*?)(?=\n|$)")
            }
            
        except Exception as e:
            logger.error(f"Error parsing workflow orchestration: {str(e)}")
            raise

    def _parse_risk_assessment(self, raw_assessment: str) -> List[RiskAssessment]:
        """Parse risk assessment into structured format."""
        try:
            risks = []
            current_risk = None
            
            for line in raw_assessment.split('\n'):
                if line.startswith('Risk:'):
                    if current_risk:
                        risks.append(current_risk)
                    current_risk = {}
                elif current_risk is not None:
                    if line.startswith('  Category:'):
                        current_risk['category'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Severity:'):
                        current_risk['severity'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Probability:'):
                        current_risk['probability'] = float(line.split(':', 1)[1].strip())
                    elif line.startswith('  Impact:'):
                        current_risk['impact'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Mitigation:'):
                        current_risk['mitigation_steps'] = [
                            step.strip() for step in line.split(':', 1)[1].strip().split(';')
                        ]
                    elif line.startswith('  Contingency:'):
                        current_risk['contingency_plan'] = line.split(':', 1)[1].strip()
                    elif line.startswith('  Owner:'):
                        current_risk['owner'] = line.split(':', 1)[1].strip()
            
            if current_risk:
                risks.append(current_risk)
            
            return [RiskAssessment(**risk) for risk in risks]
            
        except Exception as e:
            logger.error(f"Error parsing risk assessment: {str(e)}")
            raise

    def _parse_coordination(self, raw_coordination: str) -> Dict[str, Any]:
        """Parse team coordination decisions into structured format."""
        try:
            # Extract sections using regex
            actions = re.findall(r"Immediate Actions:(.*?)(?=\n\n|$)", 
                              raw_coordination, re.DOTALL)
            adjustments = re.findall(r"Resource Adjustments:(.*?)(?=\n\n|$)", 
                                  raw_coordination, re.DOTALL)
            communication = re.findall(r"Communication Needs:(.*?)(?=\n\n|$)", 
                                    raw_coordination, re.DOTALL)
            timeline = re.findall(r"Timeline Impacts:(.*?)(?=\n\n|$)", 
                               raw_coordination, re.DOTALL)
            
            return {
                "immediate_actions": self._extract_items(actions[0] if actions else "", 
                                                     r"- (.*?)(?=\n|$)"),
                "resource_adjustments": self._extract_items(adjustments[0] if adjustments else "", 
                                                        r"- (.*?)(?=\n|$)"),
                "communication_needs": self._extract_items(communication[0] if communication else "", 
                                                       r"- (.*?)(?=\n|$)"),
                "timeline_impacts": self._extract_items(timeline[0] if timeline else "", 
                                                    r"- (.*?)(?=\n|$)")
            }
            
        except Exception as e:
            logger.error(f"Error parsing team coordination: {str(e)}")
            raise

    def _extract_items(self, text: str, pattern: str) -> List[str]:
        """Extract items matching a pattern from text."""
        if not text:
            return []
        items = re.findall(pattern, text)
        return [item.strip() for item in items if item.strip()]

@click.command()
@click.option('--role-outputs', required=True, help='Path to role outputs directory')
@click.option('--validation-rules', help='Path to validation rules file')
@click.option('--conflicts-file', help='Path to conflicts file')
@click.option('--context-file', help='Path to project context file')
@click.option('--role-statuses', required=True, help='Path to role statuses file')
@click.option('--metrics-file', help='Path to project metrics file')
@click.option('--output-dir', required=True, help='Directory to save generated reports')
def main(role_outputs: str,
         validation_rules: Optional[str],
         conflicts_file: Optional[str],
         context_file: Optional[str],
         role_statuses: str,
         metrics_file: Optional[str],
         output_dir: str):
    """CLI interface for the Project Manager agent."""
    try:
        manager = ProjectManager()
        
        # Load role outputs
        outputs = {}
        for filename in os.listdir(role_outputs):
            if filename.endswith('.md'):
                filepath = os.path.join(role_outputs, filename)
                outputs[filename] = manager.load_file(filepath)
        
        # Load optional files
        rules_data = None
        if validation_rules and manager.validate_file_exists(validation_rules):
            rules_data = manager.load_file(validation_rules)
        
        conflicts_data = []
        if conflicts_file and manager.validate_file_exists(conflicts_file):
            conflicts_data = manager.load_file(conflicts_file)
        
        context_data = None
        if context_file and manager.validate_file_exists(context_file):
            context_data = manager.load_file(context_file)
        
        statuses_data = manager.load_file(role_statuses)
        
        metrics_data = None
        if metrics_file and manager.validate_file_exists(metrics_file):
            metrics_data = manager.load_file(metrics_file)
        
        # Validate cross-role outputs
        validation = manager.validate_cross_role_outputs(
            outputs,
            rules_data
        )
        manager.save_file(
            os.path.join(output_dir, 'VALIDATION_REPORT.md'),
            validation.get('content', '')
        )
        
        # Generate consensus resolution if conflicts exist
        if conflicts_data:
            resolution = manager.generate_consensus_resolution(
                conflicts_data,
                context_data
            )
            manager.save_file(
                os.path.join(output_dir, 'CONSENSUS_RESOLUTION.md'),
                resolution.get('content', '')
            )
        
        # Generate progress report
        report = manager.generate_progress_report(
            statuses_data,
            metrics_data
        )
        manager.save_file(
            os.path.join(output_dir, 'PROGRESS_REPORT.md'),
            report
        )
        
        # Orchestrate workflow
        workflow_stages = [
            WorkflowStage(
                name="Requirements Gathering",
                status="In Progress",
                roles=["Product Manager", "Business Analyst"],
                dependencies=[],
                artifacts=["Requirements Document"],
                validation_rules=["Requirements are complete"],
                completion_criteria=["Requirements are approved"]
            ),
            WorkflowStage(
                name="Design",
                status="Not Started",
                roles=["Software Architect", "UI/UX Designer"],
                dependencies=["Requirements Gathering"],
                artifacts=["Design Document"],
                validation_rules=["Design is complete"],
                completion_criteria=["Design is approved"]
            )
        ]
        orchestration = manager.orchestrate_workflow(workflow_stages)
        manager.save_file(
            os.path.join(output_dir, 'WORKFLOW_ORCHESTRATION.md'),
            yaml.dump(orchestration, default_flow_style=False)
        )
        
        # Assess project risks
        risk_assessment = manager.assess_project_risks(statuses_data, metrics_data)
        manager.save_file(
            os.path.join(output_dir, 'RISK_ASSESSMENT.md'),
            yaml.dump([risk.__dict__ for risk in risk_assessment], default_flow_style=False)
        )
        
        # Coordinate team sync
        team_sync_updates = [
            TeamSyncUpdate(
                timestamp=datetime.now(),
                role="Product Manager",
                status="In Progress",
                progress=50,
                blockers=["Waiting for design approval"],
                needs=["Design approval"],
                next_steps=["Review design document"],
                dependencies=["Design"]
            ),
            TeamSyncUpdate(
                timestamp=datetime.now(),
                role="Software Architect",
                status="Not Started",
                progress=0,
                blockers=[],
                needs=["Requirements document"],
                next_steps=["Review requirements document"],
                dependencies=["Requirements Gathering"]
            )
        ]
        coordination = manager.coordinate_team_sync(team_sync_updates)
        manager.save_file(
            os.path.join(output_dir, 'TEAM_SYNC_COORDINATION.md'),
            yaml.dump(coordination, default_flow_style=False)
        )
        
        logger.info(f"Successfully generated project management reports in: {output_dir}")
        
    except Exception as e:
        logger.error(f"Error in project manager execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
