"""
Automated checkpoint system for managing and tracking approval states across the development process.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from loguru import logger
from .approval_system import ApprovalSystem, ValidationResult, RoleFeedback

class CheckpointStatus(BaseModel):
    """Status of a checkpoint including validation results and timestamps."""
    checkpoint_id: str
    stage: str
    status: str  # 'pending', 'approved', 'rejected'
    validation_result: Optional[ValidationResult] = None
    cross_validation_results: Optional[Dict[str, RoleFeedback]] = None
    timestamp: datetime
    approved_by: Optional[List[str]] = None
    blocking_issues: Optional[List[str]] = None

class CheckpointSystem:
    def __init__(self, approval_system: ApprovalSystem):
        """Initialize the checkpoint system with an approval system instance."""
        self.approval_system = approval_system
        self.checkpoints: Dict[str, CheckpointStatus] = {}
        
    def create_checkpoint(self, checkpoint_id: str, stage: str) -> CheckpointStatus:
        """Create a new checkpoint for a specific stage."""
        checkpoint = CheckpointStatus(
            checkpoint_id=checkpoint_id,
            stage=stage,
            status="pending",
            timestamp=datetime.now()
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        logger.info(f"Created checkpoint {checkpoint_id} for stage {stage}")
        return checkpoint
    
    async def validate_checkpoint(self, 
                                checkpoint_id: str,
                                content: Dict[str, Any],
                                validation_roles: List[str],
                                context: Optional[Dict[str, Any]] = None) -> CheckpointStatus:
        """Validate a checkpoint with the approval system and cross-validate with specified roles."""
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
            
        checkpoint = self.checkpoints[checkpoint_id]
        
        try:
            # Perform main validation based on stage
            if checkpoint.stage == "product_specs":
                validation_result = await self.approval_system.validate_product_specs(content)
            elif checkpoint.stage == "architecture":
                validation_result = await self.approval_system.validate_architecture(content, context or {})
            else:
                # Default validation for other stages
                validation_result = await self.approval_system.validate_product_specs(content)
            
            checkpoint.validation_result = validation_result
            
            # Cross-validate with specified roles
            cross_validation_results = {}
            blocking_issues = []
            
            for role in validation_roles:
                feedback = await self.approval_system.cross_validate_with_role(
                    content=content,
                    role=role,
                    context=context
                )
                
                cross_validation_results[role] = feedback
                
                if feedback.concerns:
                    blocking_issues.extend(feedback.concerns)
            
            checkpoint.cross_validation_results = cross_validation_results
            checkpoint.blocking_issues = blocking_issues if blocking_issues else None
            
            # Update checkpoint status
            if validation_result.is_approved and not blocking_issues:
                checkpoint.status = "approved"
                checkpoint.approved_by = validation_roles
            else:
                checkpoint.status = "rejected"
            
            # Save validation report
            self._save_validation_report(checkpoint)
            
            return checkpoint
            
        except Exception as e:
            logger.error(f"Error validating checkpoint {checkpoint_id}: {str(e)}")
            checkpoint.status = "rejected"
            checkpoint.blocking_issues = [str(e)]
            return checkpoint
    
    def get_checkpoint_status(self, checkpoint_id: str) -> CheckpointStatus:
        """Get the current status of a checkpoint."""
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        return self.checkpoints[checkpoint_id]
    
    def _save_validation_report(self, checkpoint: CheckpointStatus) -> None:
        """Save the validation report for a checkpoint."""
        try:
            report = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "stage": checkpoint.stage,
                "status": checkpoint.status,
                "timestamp": checkpoint.timestamp.isoformat(),
                "validation_result": checkpoint.validation_result.dict() if checkpoint.validation_result else None,
                "cross_validation_results": {
                    role: feedback.dict()
                    for role, feedback in (checkpoint.cross_validation_results or {}).items()
                },
                "approved_by": checkpoint.approved_by,
                "blocking_issues": checkpoint.blocking_issues
            }
            
            # Save to validation reports directory
            from pathlib import Path
            report_dir = Path("docs/validation_reports")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = report_dir / f"checkpoint_{checkpoint.checkpoint_id}_{checkpoint.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Saved validation report to {report_path}")
            
        except Exception as e:
            logger.error(f"Error saving validation report: {str(e)}")
            raise
