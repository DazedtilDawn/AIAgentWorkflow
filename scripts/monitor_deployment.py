import click
import boto3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

class DeploymentMonitor:
    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS clients."""
        self.region = region
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
    def monitor_deployment(self, 
                         env: str, 
                         duration: int,
                         error_threshold: float = 0.05) -> bool:
        """Monitor deployment for specified duration."""
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(seconds=duration)
            
            while datetime.utcnow() < end_time:
                # Check various metrics
                metrics = self._get_metrics(env)
                logs = self._get_logs(env)
                alerts = self._check_alerts(env)
                
                # Analyze health
                health_status = self._analyze_health(metrics, logs, alerts)
                
                if not health_status['healthy']:
                    logger.error(f"Deployment health check failed: {health_status['reason']}")
                    return False
                
                # Check error rate
                if health_status['error_rate'] > error_threshold:
                    logger.error(f"Error rate ({health_status['error_rate']}) exceeds threshold ({error_threshold})")
                    return False
                
                logger.info(f"Health check passed at {datetime.utcnow()}")
                time.sleep(30)  # Wait 30 seconds between checks
            
            logger.info("Deployment monitoring completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring failed: {str(e)}")
            raise
    
    def _get_metrics(self, env: str) -> Dict:
        """Get CloudWatch metrics."""
        try:
            # Get relevant metrics for the environment
            metrics = {}
            
            # CPU Utilization
            cpu_response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'cpu',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'CPUUtilization',
                                'Dimensions': [
                                    {'Name': 'Environment', 'Value': env}
                                ]
                            },
                            'Period': 300,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow()
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
                                'MetricName': 'MemoryUtilization',
                                'Dimensions': [
                                    {'Name': 'Environment', 'Value': env}
                                ]
                            },
                            'Period': 300,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow()
            )
            metrics['memory'] = memory_response['MetricDataResults']
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise
    
    def _get_logs(self, env: str) -> List[Dict]:
        """Get CloudWatch logs."""
        try:
            log_group_name = f"/aws/ai-workflow/{env}"
            
            response = self.logs.filter_log_events(
                logGroupName=log_group_name,
                startTime=int((datetime.utcnow() - timedelta(minutes=5)).timestamp() * 1000),
                endTime=int(datetime.utcnow().timestamp() * 1000)
            )
            
            return response['events']
            
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            raise
    
    def _check_alerts(self, env: str) -> List[Dict]:
        """Check for active alerts."""
        try:
            # Implementation would check various alert sources
            # For example: CloudWatch Alarms, custom monitoring, etc.
            return []  # Simplified for example
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            raise
    
    def _analyze_health(self, 
                       metrics: Dict, 
                       logs: List[Dict], 
                       alerts: List[Dict]) -> Dict:
        """Analyze deployment health based on collected data."""
        try:
            health_status = {
                'healthy': True,
                'error_rate': 0.0,
                'reason': None
            }
            
            # Check CPU utilization
            if metrics.get('cpu'):
                cpu_values = [point['Value'] for point in metrics['cpu'] if 'Value' in point]
                if cpu_values and max(cpu_values) > 80:
                    health_status['healthy'] = False
                    health_status['reason'] = "High CPU utilization"
            
            # Check Memory utilization
            if metrics.get('memory'):
                memory_values = [point['Value'] for point in metrics['memory'] if 'Value' in point]
                if memory_values and max(memory_values) > 80:
                    health_status['healthy'] = False
                    health_status['reason'] = "High memory utilization"
            
            # Analyze logs for errors
            error_count = sum(1 for log in logs if 'ERROR' in log.get('message', ''))
            total_logs = len(logs) if logs else 1
            health_status['error_rate'] = error_count / total_logs
            
            # Check alerts
            if alerts:
                health_status['healthy'] = False
                health_status['reason'] = f"Active alerts: {len(alerts)}"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error analyzing health: {str(e)}")
            raise

@click.command()
@click.option('--env', required=True, type=click.Choice(['staging', 'production']), 
              help='Environment to monitor')
@click.option('--duration', default=300, help='Monitoring duration in seconds')
@click.option('--error-threshold', default=0.05, help='Maximum acceptable error rate')
@click.option('--region', default='us-east-1', help='AWS region')
def main(env: str, duration: int, error_threshold: float, region: str):
    """CLI interface for deployment monitoring."""
    try:
        monitor = DeploymentMonitor(region)
        success = monitor.monitor_deployment(env, duration, error_threshold)
        
        if not success:
            raise Exception("Deployment monitoring failed")
            
    except Exception as e:
        logger.error(f"Monitoring failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
