import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import json
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from loguru import logger
import asyncio
import re
from dataclasses import dataclass
import yaml
import subprocess
import psutil
import numpy as np
from scipy import stats

class DeploymentConfig(BaseModel):
    environment: str
    version: str
    services: List[str]
    dependencies: Dict[str, str]
    env_vars: Dict[str, str]
    rollback_version: Optional[str]
    health_checks: Dict[str, str]
    monitoring_config: Dict[str, Any]
    alert_thresholds: Dict[str, float]

class ServiceMetrics(BaseModel):
    service_name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    request_count: int
    timestamp: datetime

class Anomaly(BaseModel):
    service: str
    metric: str
    value: float
    threshold: float
    timestamp: datetime
    severity: str
    description: str

class DeploymentStatus(BaseModel):
    version: str
    environment: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    services_status: Dict[str, str]
    metrics: List[ServiceMetrics]
    anomalies: List[Anomaly]
    logs: List[str]

class RollbackTrigger(BaseModel):
    service: str
    reason: str
    metrics: Dict[str, float]
    timestamp: datetime
    affected_components: List[str]
    recovery_steps: List[str]

@dataclass
class DeploymentReport:
    timestamp: datetime
    environment: str
    version: str
    status: str
    duration: float
    services_deployed: List[str]
    configuration_changes: Dict[str, Any]
    metrics_summary: Dict[str, Dict[str, float]]
    anomalies_detected: List[Anomaly]
    rollbacks_performed: List[RollbackTrigger]
    recommendations: List[str]

class DevOpsManager:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the DevOps Manager with AI configuration."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize deployment directory
        self.deploy_dir = Path(__file__).parent / "deployments"
        self.deploy_dir.mkdir(exist_ok=True)
        
        # Initialize metrics history
        self.metrics_history: Dict[str, List[ServiceMetrics]] = {}
        
    async def generate_deployment_config(self, 
                                      architecture: Dict[str, Any],
                                      environment: str) -> DeploymentConfig:
        """Generate deployment configuration based on architecture."""
        try:
            # Prepare deployment prompt
            deploy_prompt = f"""Generate deployment configuration for:

            Architecture:
            {json.dumps(architecture, indent=2)}

            Environment: {environment}

            Include:
            1. Service definitions
            2. Dependencies
            3. Environment variables
            4. Health checks
            5. Monitoring configuration
            6. Alert thresholds
            7. Rollback strategy

            Return as JSON matching DeploymentConfig model.
            """

            response = await self.client.generate_content(deploy_prompt)
            config_data = json.loads(response.text)
            
            return DeploymentConfig(**config_data)
            
        except Exception as e:
            logger.error(f"Error generating deployment config: {str(e)}")
            raise

    async def deploy_services(self, 
                            config: DeploymentConfig) -> DeploymentStatus:
        """Deploy services based on configuration."""
        try:
            start_time = datetime.now()
            status = DeploymentStatus(
                version=config.version,
                environment=config.environment,
                status="in_progress",
                start_time=start_time,
                end_time=None,
                services_status={},
                metrics=[],
                anomalies=[],
                logs=[]
            )
            
            # Deploy each service
            for service in config.services:
                try:
                    # Simulate service deployment
                    # In reality, this would use Docker, Kubernetes, etc.
                    logger.info(f"Deploying {service}...")
                    await asyncio.sleep(2)  # Simulate deployment time
                    
                    # Update environment variables
                    os.environ.update(config.env_vars)
                    
                    # Perform health check
                    health_endpoint = config.health_checks.get(service)
                    if health_endpoint:
                        # Simulate health check
                        is_healthy = True  # Would actually check endpoint
                        
                        if is_healthy:
                            status.services_status[service] = "healthy"
                        else:
                            status.services_status[service] = "unhealthy"
                            raise Exception(f"Health check failed for {service}")
                    
                    # Collect initial metrics
                    metrics = await self.collect_service_metrics(service)
                    status.metrics.append(metrics)
                    
                    # Store metrics in history
                    if service not in self.metrics_history:
                        self.metrics_history[service] = []
                    self.metrics_history[service].append(metrics)
                    
                except Exception as e:
                    logger.error(f"Error deploying {service}: {str(e)}")
                    status.services_status[service] = "failed"
                    status.logs.append(f"Failed to deploy {service}: {str(e)}")
                    
                    # Trigger rollback if needed
                    if config.rollback_version:
                        await self.rollback_deployment(
                            config,
                            RollbackTrigger(
                                service=service,
                                reason=str(e),
                                metrics={},
                                timestamp=datetime.now(),
                                affected_components=[service],
                                recovery_steps=[
                                    f"Rollback {service} to version {config.rollback_version}"
                                ]
                            )
                        )
            
            # Update final status
            status.end_time = datetime.now()
            if all(s == "healthy" for s in status.services_status.values()):
                status.status = "success"
            else:
                status.status = "partial_failure"
            
            return status
            
        except Exception as e:
            logger.error(f"Error in deployment: {str(e)}")
            raise

    async def collect_service_metrics(self, 
                                    service: str) -> ServiceMetrics:
        """Collect performance metrics for a service."""
        try:
            # Simulate metric collection
            # In reality, would use Prometheus, Grafana, etc.
            return ServiceMetrics(
                service_name=service,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                response_time=np.random.normal(100, 20),  # Simulated ms
                error_rate=np.random.random() * 0.1,  # Simulated 0-10%
                request_count=int(np.random.normal(1000, 200)),  # Simulated
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {service}: {str(e)}")
            raise

    async def detect_anomalies(self, 
                             metrics: List[ServiceMetrics],
                             thresholds: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies in service metrics."""
        try:
            anomalies = []
            
            for metric in metrics:
                # Get historical metrics for the service
                history = self.metrics_history.get(metric.service_name, [])
                if len(history) < 10:  # Need enough history for detection
                    continue
                
                # Calculate z-scores for each metric
                historical_values = {
                    "cpu_usage": [m.cpu_usage for m in history],
                    "memory_usage": [m.memory_usage for m in history],
                    "response_time": [m.response_time for m in history],
                    "error_rate": [m.error_rate for m in history]
                }
                
                current_values = {
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "response_time": metric.response_time,
                    "error_rate": metric.error_rate
                }
                
                for metric_name, current_value in current_values.items():
                    historical = historical_values[metric_name]
                    z_score = abs(stats.zscore([current_value] + historical))[0]
                    threshold = thresholds.get(metric_name, 3.0)  # Default 3 sigma
                    
                    if z_score > threshold:
                        severity = "critical" if z_score > threshold * 1.5 else "warning"
                        
                        anomalies.append(Anomaly(
                            service=metric.service_name,
                            metric=metric_name,
                            value=current_value,
                            threshold=threshold,
                            timestamp=datetime.now(),
                            severity=severity,
                            description=f"Anomalous {metric_name}: {current_value:.2f} (z-score: {z_score:.2f})"
                        ))
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise

    async def rollback_deployment(self, 
                                config: DeploymentConfig,
                                trigger: RollbackTrigger) -> bool:
        """Rollback deployment to previous version."""
        try:
            if not config.rollback_version:
                logger.error("No rollback version specified")
                return False
            
            logger.info(f"Rolling back {trigger.service} to {config.rollback_version}")
            
            # Simulate rollback
            # In reality, would use container orchestration, etc.
            await asyncio.sleep(2)  # Simulate rollback time
            
            # Verify rollback
            metrics = await self.collect_service_metrics(trigger.service)
            is_healthy = metrics.error_rate < 0.1  # Simple health check
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Error in rollback: {str(e)}")
            raise

    async def deploy_system(self, implementation: str, test_results: str) -> str:
        """Wrapper method for integration test compatibility."""
        try:
            # Execute deployment process
            deployment = await self.execute_deployment({
                'implementation': implementation,
                'test_results': test_results
            })
            return deployment.to_markdown()
            
        except Exception as e:
            logger.error(f"Error in deploy_system: {str(e)}")
            raise

    def generate_deployment_report(self,
                                 status: DeploymentStatus,
                                 config: DeploymentConfig) -> DeploymentReport:
        """Generate comprehensive deployment report."""
        try:
            # Calculate metrics summary
            metrics_summary = {}
            for service in config.services:
                service_metrics = [m for m in status.metrics if m.service_name == service]
                if service_metrics:
                    metrics_summary[service] = {
                        "avg_cpu": np.mean([m.cpu_usage for m in service_metrics]),
                        "avg_memory": np.mean([m.memory_usage for m in service_metrics]),
                        "avg_response": np.mean([m.response_time for m in service_metrics]),
                        "error_rate": np.mean([m.error_rate for m in service_metrics])
                    }
            
            # Generate recommendations
            recommendations = []
            
            # Performance recommendations
            for service, metrics in metrics_summary.items():
                if metrics["avg_cpu"] > 80:
                    recommendations.append(
                        f"Consider scaling {service} due to high CPU usage ({metrics['avg_cpu']:.1f}%)"
                    )
                if metrics["avg_memory"] > 80:
                    recommendations.append(
                        f"Optimize memory usage for {service} ({metrics['avg_memory']:.1f}%)"
                    )
                if metrics["avg_response"] > 200:
                    recommendations.append(
                        f"Investigate high response times in {service} ({metrics['avg_response']:.1f}ms)"
                    )
            
            # Anomaly recommendations
            for anomaly in status.anomalies:
                if anomaly.severity == "critical":
                    recommendations.append(
                        f"Urgent: Address {anomaly.metric} anomaly in {anomaly.service}"
                    )
            
            # Configuration recommendations
            if len(config.services) > 5 and not config.monitoring_config.get("distributed_tracing"):
                recommendations.append(
                    "Enable distributed tracing for better visibility across services"
                )
            
            return DeploymentReport(
                timestamp=datetime.now(),
                environment=config.environment,
                version=config.version,
                status=status.status,
                duration=(status.end_time - status.start_time).total_seconds(),
                services_deployed=config.services,
                configuration_changes={
                    "env_vars": config.env_vars,
                    "dependencies": config.dependencies
                },
                metrics_summary=metrics_summary,
                anomalies_detected=status.anomalies,
                rollbacks_performed=[],  # Would be populated from actual rollbacks
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating deployment report: {str(e)}")
            raise

    def save_deployment_log(self,
                          report: DeploymentReport,
                          base_dir: str):
        """Save deployment log to file."""
        try:
            base_path = Path(base_dir)
            logs_dir = base_path / "deployment_logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Generate log filename
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"deployment_{timestamp}.md"
            
            # Format rollbacks section
            rollbacks_text = ""
            for rollback in report.rollbacks_performed:
                recovery_steps = "\n".join(f"    - {step}" for step in rollback.recovery_steps)
                rollbacks_text += f"""
- **{rollback.service}**
  - Reason: {rollback.reason}
  - Affected Components: {", ".join(rollback.affected_components)}
  - Recovery Steps:
{recovery_steps}
"""

            # Format recommendations
            recommendations = "\n".join(f"- {rec}" for rec in report.recommendations)

            # Write deployment log
            log_file.write_text(f"""# Deployment Report

## Overview
- Timestamp: {report.timestamp}
- Environment: {report.environment}
- Version: {report.version}
- Status: {report.status}
- Duration: {report.duration:.2f}s

## Services Deployed
{", ".join(report.services_deployed)}

## Configuration Changes
{json.dumps(report.configuration_changes, indent=2)}

## Metrics Summary
{json.dumps(report.metrics_summary, indent=2)}

## Anomalies Detected
{self._format_anomalies(report.anomalies_detected)}

## Rollbacks Performed
{rollbacks_text}

## Recommendations
{recommendations}
""")

            logger.info(f"Deployment log saved to {log_file}")
            
        except Exception as e:
            logger.error(f"Error saving deployment log: {str(e)}")
            raise
