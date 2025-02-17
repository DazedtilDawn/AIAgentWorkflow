import click
import boto3
import os
from typing import Optional
from loguru import logger

class Deployer:
    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS clients."""
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudformation = boto3.client('cloudformation', region_name=region)
    
    def deploy_to_environment(self, 
                            env: str, 
                            code_dir: str,
                            stack_name: Optional[str] = None) -> bool:
        """Deploy application to specified environment."""
        try:
            # Validate environment
            if env not in ['staging', 'production']:
                raise ValueError(f"Invalid environment: {env}")
            
            # Generate stack name if not provided
            if not stack_name:
                stack_name = f"ai-workflow-{env}"
            
            # Package application
            artifact_path = self._package_application(code_dir)
            
            # Upload to S3
            bucket_name = f"ai-workflow-artifacts-{env}"
            s3_key = f"deployments/{os.path.basename(artifact_path)}"
            self._upload_to_s3(artifact_path, bucket_name, s3_key)
            
            # Deploy using CloudFormation
            template_url = f"https://{bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            self._deploy_stack(stack_name, template_url, env)
            
            logger.info(f"Successfully deployed to {env} environment")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
    
    def _package_application(self, code_dir: str) -> str:
        """Package application code for deployment."""
        try:
            # Implementation would create deployment package
            # For example: ZIP file, Docker image, etc.
            return "/tmp/app-package.zip"  # Simplified for example
        except Exception as e:
            logger.error(f"Error packaging application: {str(e)}")
            raise
    
    def _upload_to_s3(self, 
                     file_path: str, 
                     bucket_name: str, 
                     s3_key: str) -> None:
        """Upload deployment package to S3."""
        try:
            # Ensure bucket exists
            self.s3.head_bucket(Bucket=bucket_name)
            
            # Upload file
            with open(file_path, 'rb') as f:
                self.s3.upload_fileobj(f, bucket_name, s3_key)
                
            logger.info(f"Successfully uploaded deployment package to S3: {s3_key}")
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise
    
    def _deploy_stack(self, 
                     stack_name: str, 
                     template_url: str, 
                     env: str) -> None:
        """Deploy CloudFormation stack."""
        try:
            # Check if stack exists
            try:
                self.cloudformation.describe_stacks(StackName=stack_name)
                update_stack = True
            except self.cloudformation.exceptions.ClientError:
                update_stack = False
            
            # Set stack parameters based on environment
            parameters = [
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': env
                },
                {
                    'ParameterKey': 'InstanceType',
                    'ParameterValue': 't3.micro' if env == 'staging' else 't3.small'
                }
            ]
            
            if update_stack:
                self.cloudformation.update_stack(
                    StackName=stack_name,
                    TemplateURL=template_url,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_IAM']
                )
            else:
                self.cloudformation.create_stack(
                    StackName=stack_name,
                    TemplateURL=template_url,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_IAM']
                )
            
            logger.info(f"Successfully {'updated' if update_stack else 'created'} stack: {stack_name}")
            
        except Exception as e:
            logger.error(f"Error deploying stack: {str(e)}")
            raise

@click.command()
@click.option('--env', required=True, type=click.Choice(['staging', 'production']), 
              help='Target environment for deployment')
@click.option('--code-dir', required=True, help='Directory containing application code')
@click.option('--stack-name', help='Optional CloudFormation stack name')
@click.option('--region', default='us-east-1', help='AWS region for deployment')
def main(env: str, code_dir: str, stack_name: Optional[str], region: str):
    """CLI interface for deployment."""
    try:
        deployer = Deployer(region)
        deployer.deploy_to_environment(env, code_dir, stack_name)
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
