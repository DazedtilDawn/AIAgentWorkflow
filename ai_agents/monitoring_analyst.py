import click
import json
from datetime import datetime, timedelta
import boto3
from loguru import logger
from typing import Dict, List, Optional
from .base_agent import BaseAgent

class MonitoringAnalyst(BaseAgent):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(model)
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
    
    async def analyze_metrics(self, 
                            metrics_data: Dict,
                            historical_data: Optional[Dict] = None) -> Dict:
        """Analyze system metrics and identify patterns/anomalies."""
        system_message = """You are an AIOps Analyst specializing in system metrics 
        analysis. Focus on identifying patterns, anomalies, and performance insights."""
        
        context = f"Historical data:\n{historical_data}\n" if historical_data else ""
        prompt = f"""{context}
        Analyze the following metrics data:

        {metrics_data}

        Provide insights on:
        1. Performance Patterns
           - Resource utilization trends
           - Bottlenecks and constraints
           - Scaling patterns
        2. Anomalies
           - Unusual behavior
           - Potential issues
           - Root cause indicators
        3. Optimization Opportunities
           - Resource allocation
           - Caching strategies
           - Architecture improvements
        4. Predictive Insights
           - Capacity planning
           - Trend forecasting
           - Risk assessment
        """
        
        try:
            analysis = await self.get_completion(prompt, system_message, temperature=0.6)
            return self._parse_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing metrics: {str(e)}")
            raise
    
    async def analyze_user_behavior(self, 
                                  interaction_logs: List[Dict]) -> Dict:
        """Analyze user interaction patterns and behavior."""
        system_message = """You are a User Behavior Analyst specializing in 
        understanding user interaction patterns and identifying UX improvements."""
        
        prompt = f"""Analyze the following user interaction logs:

        {interaction_logs}

        Provide insights on:
        1. User Patterns
           - Common workflows
           - Feature usage
           - Session characteristics
        2. Pain Points
           - Error frequencies
           - Abandoned actions
           - Performance impact
        3. UX Improvements
           - Workflow optimizations
           - Interface enhancements
           - Feature suggestions
        4. Behavioral Segments
           - User categories
           - Usage patterns
           - Preference clusters
        """
        
        try:
            analysis = await self.get_completion(prompt, system_message, temperature=0.7)
            return self._parse_behavior_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            raise
    
    def collect_metrics(self, 
                       start_time: datetime,
                       end_time: datetime) -> Dict:
        """Collect system metrics from CloudWatch."""
        try:
            metrics = {}
            
            # CPU Utilization
            cpu_response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'cpu',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'CPUUtilization'
                            },
                            'Period': 300,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            metrics['cpu'] = cpu_response['MetricDataResults']
            
            # Memory Utilization
            memory_response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'memory',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'MemoryUtilization'
                            },
                            'Period': 300,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            metrics['memory'] = memory_response['MetricDataResults']
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            raise
    
    def collect_logs(self,
                    start_time: datetime,
                    end_time: datetime,
                    log_group: str) -> List[Dict]:
        """Collect application logs from CloudWatch Logs."""
        try:
            logs = []
            paginator = self.logs.get_paginator('filter_log_events')
            
            for page in paginator.paginate(
                logGroupName=log_group,
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000)
            ):
                logs.extend(page['events'])
            
            return logs
            
        except Exception as e:
            logger.error(f"Error collecting logs: {str(e)}")
            raise
    
    def _parse_analysis(self, raw_analysis: str) -> Dict:
        """Parse the raw metrics analysis into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_analysis}  # Simplified for example
    
    def _parse_behavior_analysis(self, raw_analysis: str) -> Dict:
        """Parse the raw behavior analysis into structured format."""
        # Implementation would parse the text into structured data
        return {"content": raw_analysis}  # Simplified for example
    
    def _generate_monitoring_report(self,
                                  metrics_analysis: Dict,
                                  behavior_analysis: Dict) -> str:
        """Generate comprehensive monitoring report."""
        report = ["# System Monitoring Report\n\n"]
        
        # Add metrics analysis
        report.append("## System Metrics Analysis\n")
        report.append(metrics_analysis.get('content', ''))
        
        # Add behavior analysis
        report.append("\n## User Behavior Analysis\n")
        report.append(behavior_analysis.get('content', ''))
        
        # Add recommendations
        report.append("\n## Recommendations\n")
        for rec in metrics_analysis.get('recommendations', []):
            report.append(f"- {rec}\n")
        for rec in behavior_analysis.get('recommendations', []):
            report.append(f"- {rec}\n")
        
        return "".join(report)

@click.command()
@click.option('--output', required=True, help='Path to save the monitoring report')
@click.option('--duration', default=3600, help='Analysis duration in seconds')
@click.option('--log-group', required=True, help='CloudWatch Log Group name')
def main(output: str, duration: int, log_group: str):
    """CLI interface for the Monitoring Analyst."""
    try:
        analyst = MonitoringAnalyst()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=duration)
        
        # Collect data
        metrics = analyst.collect_metrics(start_time, end_time)
        logs = analyst.collect_logs(start_time, end_time, log_group)
        
        # Analyze data
        metrics_analysis = analyst.analyze_metrics(metrics)
        behavior_analysis = analyst.analyze_user_behavior(logs)
        
        # Generate and save report
        report = analyst._generate_monitoring_report(
            metrics_analysis,
            behavior_analysis
        )
        analyst.save_file(output, report)
        
        logger.info(f"Successfully generated monitoring report: {output}")
        
    except Exception as e:
        logger.error(f"Error in monitoring analyst execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
