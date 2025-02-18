import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from loguru import logger
import asyncio
import numpy as np
from scipy import stats
import pandas as pd
from dataclasses import dataclass
from collections import defaultdict

class UserInteraction(BaseModel):
    timestamp: datetime
    user_id: str
    action: str
    component: str
    duration: float
    success: bool
    error_message: Optional[str]
    metadata: Dict[str, Any]

class PerformanceMetric(BaseModel):
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    component: str
    context: Dict[str, Any]

class SystemHealth(BaseModel):
    timestamp: datetime
    status: str
    components: Dict[str, str]
    resource_usage: Dict[str, float]
    active_users: int
    error_count: int
    warning_count: int

class Insight(BaseModel):
    category: str
    severity: str
    description: str
    metrics: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class MonitoringReport:
    period_start: datetime
    period_end: datetime
    system_health: SystemHealth
    key_metrics: Dict[str, Dict[str, float]]
    user_patterns: Dict[str, Any]
    performance_insights: List[Insight]
    security_insights: List[Insight]
    optimization_suggestions: List[str]
    anomalies_detected: List[Dict[str, Any]]

class MonitoringAnalytics:
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the Monitoring & Analytics system."""
        self.model = model
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Initialize data storage
        self.monitoring_dir = Path(__file__).parent / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)
        
        # Initialize metric storage
        self.performance_metrics: List[PerformanceMetric] = []
        self.user_interactions: List[UserInteraction] = []
        self.system_health_history: List[SystemHealth] = []
        
        # Configure monitoring windows
        self.short_window = timedelta(minutes=5)
        self.medium_window = timedelta(hours=1)
        self.long_window = timedelta(days=1)

    async def track_user_interaction(self, interaction: UserInteraction):
        """Track and analyze user interactions."""
        try:
            self.user_interactions.append(interaction)
            
            # Analyze patterns in recent interactions
            recent = [i for i in self.user_interactions 
                     if i.timestamp > datetime.now() - self.short_window]
            
            # Check for potential issues
            if interaction.success is False:
                await self.analyze_error_pattern(interaction, recent)
                
            # Update user behavior models
            await self.update_user_patterns(recent)
            
        except Exception as e:
            logger.error(f"Error tracking user interaction: {str(e)}")
            raise

    async def record_performance_metric(self, metric: PerformanceMetric):
        """Record and analyze performance metrics."""
        try:
            self.performance_metrics.append(metric)
            
            # Analyze recent metrics for anomalies
            component_metrics = [m for m in self.performance_metrics 
                               if m.component == metric.component
                               and m.metric_name == metric.metric_name
                               and m.timestamp > datetime.now() - self.medium_window]
            
            if len(component_metrics) > 10:
                values = [m.value for m in component_metrics]
                z_score = abs(stats.zscore(values)[-1])
                
                if z_score > 3:  # 3 sigma threshold
                    await self.handle_metric_anomaly(metric, z_score)
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {str(e)}")
            raise

    async def update_system_health(self, health: SystemHealth):
        """Update and analyze system health status."""
        try:
            self.system_health_history.append(health)
            
            # Analyze health trends
            recent_health = [h for h in self.system_health_history
                           if h.timestamp > datetime.now() - self.short_window]
            
            # Check for degradation
            if health.status != "healthy":
                await self.analyze_health_degradation(health, recent_health)
            
            # Update resource usage trends
            await self.analyze_resource_trends(recent_health)
            
        except Exception as e:
            logger.error(f"Error updating system health: {str(e)}")
            raise

    async def analyze_error_pattern(self, 
                                  current: UserInteraction,
                                  recent: List[UserInteraction]) -> Optional[Insight]:
        """Analyze patterns in error occurrences."""
        try:
            # Group errors by component
            errors_by_component = defaultdict(list)
            for interaction in recent:
                if interaction.success is False:
                    errors_by_component[interaction.component].append(interaction)
            
            # Check for error clusters
            if len(errors_by_component[current.component]) > 3:
                return Insight(
                    category="error_pattern",
                    severity="high",
                    description=f"Multiple errors detected in {current.component}",
                    metrics={
                        "error_count": len(errors_by_component[current.component]),
                        "error_rate": len(errors_by_component[current.component]) / len(recent)
                    },
                    recommendations=[
                        f"Investigate {current.component} for potential issues",
                        "Review error logs for common patterns",
                        "Consider temporary failover if errors persist"
                    ],
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing error pattern: {str(e)}")
            raise

    async def analyze_health_degradation(self,
                                       current: SystemHealth,
                                       history: List[SystemHealth]) -> Optional[Insight]:
        """Analyze system health degradation patterns."""
        try:
            # Calculate health metrics
            error_trend = [h.error_count for h in history]
            resource_trend = {
                resource: [h.resource_usage.get(resource, 0) for h in history]
                for resource in current.resource_usage.keys()
            }
            
            # Check for concerning patterns
            concerns = []
            if np.mean(error_trend) > 10:
                concerns.append(f"High error rate: {np.mean(error_trend):.1f} errors/interval")
            
            for resource, values in resource_trend.items():
                if np.mean(values) > 80:
                    concerns.append(f"High {resource} usage: {np.mean(values):.1f}%")
            
            if concerns:
                return Insight(
                    category="health_degradation",
                    severity="high" if len(concerns) > 2 else "medium",
                    description="System health degradation detected",
                    metrics={
                        "avg_errors": float(np.mean(error_trend)),
                        **{f"avg_{r}_usage": float(np.mean(v)) 
                           for r, v in resource_trend.items()}
                    },
                    recommendations=[
                        "Review system logs for error patterns",
                        "Check resource allocation and scaling policies",
                        "Consider proactive scaling if resource usage remains high"
                    ] + [f"Address: {concern}" for concern in concerns],
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing health degradation: {str(e)}")
            raise

    async def analyze_resource_trends(self,
                                    health_history: List[SystemHealth]) -> Dict[str, Any]:
        """Analyze resource usage trends and patterns."""
        try:
            if not health_history:
                return {}
            
            # Extract resource usage over time
            resources = health_history[0].resource_usage.keys()
            usage_trends = {
                resource: [h.resource_usage.get(resource, 0) for h in health_history]
                for resource in resources
            }
            
            # Calculate trends and patterns
            analysis = {}
            for resource, values in usage_trends.items():
                if len(values) < 2:
                    continue
                    
                # Calculate basic statistics
                mean_usage = np.mean(values)
                std_usage = np.std(values)
                trend = np.polyfit(range(len(values)), values, 1)[0]
                
                analysis[resource] = {
                    "current": values[-1],
                    "mean": mean_usage,
                    "std": std_usage,
                    "trend": trend,
                    "status": "stable"
                }
                
                # Determine status
                if trend > 0.1:  # Significant upward trend
                    analysis[resource]["status"] = "increasing"
                elif trend < -0.1:  # Significant downward trend
                    analysis[resource]["status"] = "decreasing"
                
                # Check for concerning patterns
                if mean_usage > 80:
                    analysis[resource]["warning"] = "High average usage"
                elif trend > 0.2:
                    analysis[resource]["warning"] = "Rapid increase in usage"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing resource trends: {str(e)}")
            raise

    async def handle_metric_anomaly(self,
                                  metric: PerformanceMetric,
                                  severity: float) -> None:
        """Handle detected metric anomalies."""
        try:
            # Generate anomaly description
            description = await self.generate_anomaly_description(metric, severity)
            
            # Create insight
            insight = Insight(
                category="metric_anomaly",
                severity="high" if severity > 4 else "medium",
                description=description,
                metrics={
                    "value": metric.value,
                    "z_score": severity
                },
                recommendations=[
                    f"Investigate {metric.component} for performance issues",
                    "Review recent changes that might affect this metric",
                    "Consider adjusting monitoring thresholds if needed"
                ],
                timestamp=datetime.now()
            )
            
            # Log the anomaly
            logger.warning(f"Metric anomaly detected: {description}")
            
            # Save for reporting
            await self.save_insight(insight)
            
        except Exception as e:
            logger.error(f"Error handling metric anomaly: {str(e)}")
            raise

    async def generate_anomaly_description(self,
                                         metric: PerformanceMetric,
                                         severity: float) -> str:
        """Generate human-readable anomaly description using AI."""
        try:
            prompt = f"""Generate a clear, concise description of a metric anomaly:

            Metric: {metric.metric_name}
            Component: {metric.component}
            Value: {metric.value} {metric.unit}
            Severity (z-score): {severity}
            Context: {json.dumps(metric.context, indent=2)}

            Focus on:
            1. What is unusual about the metric
            2. Potential impact on the system
            3. Level of concern

            Return a single paragraph, technical but accessible.
            """

            response = await self.client.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating anomaly description: {str(e)}")
            raise

    async def update_user_patterns(self,
                                 recent_interactions: List[UserInteraction]) -> None:
        """Update and analyze user behavior patterns."""
        try:
            if not recent_interactions:
                return
            
            # Group interactions by user
            user_patterns = defaultdict(list)
            for interaction in recent_interactions:
                user_patterns[interaction.user_id].append(interaction)
            
            # Analyze patterns for each user
            for user_id, interactions in user_patterns.items():
                # Calculate success rate
                success_rate = sum(1 for i in interactions if i.success) / len(interactions)
                
                # Analyze common actions
                action_counts = defaultdict(int)
                for interaction in interactions:
                    action_counts[interaction.action] += 1
                
                # Calculate average duration
                avg_duration = np.mean([i.duration for i in interactions])
                
                # Check for potential issues
                if success_rate < 0.8:
                    await self.handle_user_difficulty(user_id, interactions)
                
                if avg_duration > 5.0:  # Threshold in seconds
                    await self.analyze_performance_impact(user_id, interactions)
            
        except Exception as e:
            logger.error(f"Error updating user patterns: {str(e)}")
            raise

    async def generate_monitoring_report(self,
                                       period: timedelta = timedelta(hours=1)) -> MonitoringReport:
        """Generate comprehensive monitoring report."""
        try:
            now = datetime.now()
            period_start = now - period
            
            # Get relevant data
            recent_health = [h for h in self.system_health_history
                           if h.timestamp > period_start]
            recent_metrics = [m for m in self.performance_metrics
                            if m.timestamp > period_start]
            recent_interactions = [i for i in self.user_interactions
                                 if i.timestamp > period_start]
            
            # Calculate key metrics
            key_metrics = {
                "system": {
                    "avg_error_rate": np.mean([h.error_count for h in recent_health]),
                    "avg_active_users": np.mean([h.active_users for h in recent_health]),
                    "peak_resource_usage": max(
                        max(h.resource_usage.values()) for h in recent_health
                    ) if recent_health else 0
                },
                "performance": {
                    metric_name: np.mean([
                        m.value for m in recent_metrics if m.metric_name == metric_name
                    ])
                    for metric_name in set(m.metric_name for m in recent_metrics)
                },
                "user": {
                    "success_rate": sum(1 for i in recent_interactions if i.success) 
                                  / len(recent_interactions) if recent_interactions else 1.0,
                    "avg_duration": np.mean([i.duration for i in recent_interactions])
                                   if recent_interactions else 0
                }
            }
            
            # Generate insights
            performance_insights = await self.analyze_performance_insights(recent_metrics)
            security_insights = await self.analyze_security_insights(recent_interactions)
            
            # Generate optimization suggestions
            suggestions = await self.generate_optimization_suggestions(
                key_metrics, recent_health[-1] if recent_health else None
            )
            
            # Detect anomalies
            anomalies = await self.detect_system_anomalies(
                recent_metrics, recent_health, recent_interactions
            )
            
            return MonitoringReport(
                period_start=period_start,
                period_end=now,
                system_health=recent_health[-1] if recent_health else None,
                key_metrics=key_metrics,
                user_patterns=await self.analyze_user_patterns(recent_interactions),
                performance_insights=performance_insights,
                security_insights=security_insights,
                optimization_suggestions=suggestions,
                anomalies_detected=anomalies
            )
            
        except Exception as e:
            logger.error(f"Error generating monitoring report: {str(e)}")
            raise

    async def generate_report(self, deployment: str, test_results: str) -> str:
        """Wrapper method for integration test compatibility."""
        try:
            # Generate monitoring report
            report = await self.analyze_system_health({
                'deployment': deployment,
                'test_results': test_results
            })
            return report.to_markdown()
            
        except Exception as e:
            logger.error(f"Error in generate_report: {str(e)}")
            raise

    def save_monitoring_report(self,
                             report: MonitoringReport,
                             base_dir: str) -> None:
        """Save monitoring report to file."""
        try:
            base_path = Path(base_dir)
            reports_dir = base_path / "monitoring_reports"
            reports_dir.mkdir(exist_ok=True)
            
            # Generate report filename
            timestamp = report.period_end.strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"monitoring_report_{timestamp}.md"
            
            # Format sections
            user_patterns = "\n".join(f"- {pattern}" for pattern in report.user_patterns.values())
            optimization_suggestions = "\n".join(f"- {suggestion}" for suggestion in report.optimization_suggestions)

            # Format anomalies section
            anomalies_text = ""
            for anomaly in report.anomalies_detected:
                anomalies_text += f"""
### {anomaly['category']}
- Component: {anomaly['component']}
- Description: {anomaly['description']}
- Severity: {anomaly['severity']}
- Detected at: {anomaly['timestamp']}
"""

            # Write monitoring report
            report_file.write_text(f"""# Monitoring Report

## System Health Overview
- Status: {report.system_health.status}
- Active Users: {report.system_health.active_users}
- Error Count: {report.system_health.error_count}
- Warning Count: {report.system_health.warning_count}

## Resource Usage
{json.dumps(report.system_health.resource_usage, indent=2)}

## Key Metrics
{json.dumps(report.key_metrics, indent=2)}

## User Behavior Patterns
{user_patterns}

## Optimization Suggestions
{optimization_suggestions}

## Detected Anomalies
{anomalies_text}
""")

            logger.info(f"Monitoring report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving monitoring report: {str(e)}")
            raise
