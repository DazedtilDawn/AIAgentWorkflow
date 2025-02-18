# GitHub Repository Setup Guide

This guide outlines the required configuration for the Multi-Role Pipeline workflow.

## Environment Configuration

### 1. Create Environments
Go to **Settings** → **Environments** and create the following environments:

#### Staging Environment
1. Click "New environment"
2. Name: `staging` (exactly as shown)
3. Configure environment protection rules:
   - No required reviewers
   - No wait timer
   - Allow all branches to deploy

#### Production Environment
1. Click "New environment"
2. Name: `production` (exactly as shown)
3. Configure environment protection rules:
   - Required reviewers: 1
   - Wait timer: 10 minutes
   - Deployment branch: `main` only

### 2. Configure Environment URLs
For each environment, set the environment URL:
- Staging: https://dev.example.com
- Production: https://prod.example.com

## Variables and Secrets Configuration

### Repository Variables
Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** and add:

1. `PYTHON_VERSION`
   - Name: `PYTHON_VERSION`
   - Value: `3.10`
   - Used for Python setup in all jobs

2. `AWS_REGION`
   - Name: `AWS_REGION`
   - Value: `us-east-1`
   - Used for AWS service configuration

### Repository Secrets
Go to **Settings** → **Secrets and variables** → **Actions** → **Secrets** and add:

1. `GEMINI_API_KEY`
   - Name: `GEMINI_API_KEY`
   - Value: Your Gemini AI API key
   - Used by all AI agents for content generation

2. `AWS_ACCESS_KEY_ID`
   - Name: `AWS_ACCESS_KEY_ID`
   - Value: Your AWS access key ID
   - Used for AWS authentication

3. `AWS_SECRET_ACCESS_KEY`
   - Name: `AWS_SECRET_ACCESS_KEY`
   - Value: Your AWS secret access key
   - Used for AWS authentication

## AWS Configuration

### Create IAM User
1. Go to AWS IAM Console
2. Create new user: `github-actions`
3. Attach policies:
   - AmazonS3ReadWrite
   - CloudWatchLogsFullAccess
   - Any other required service permissions
4. Generate access keys
5. Save the access key ID and secret key
6. Add to GitHub repository secrets

## Branch Protection Rules

### Main Branch Protection
Go to **Settings** → **Branches** and add a rule for `main`:

1. Click "Add branch protection rule"
2. Branch name pattern: `main`
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require conversation resolution
   - Include administrators
   - Allow force pushes: Disable
   - Allow deletions: Disable

## Workflow Permissions

### Configure Workflow Permissions
1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Enable "Read and write permissions"
   - Enable "Allow GitHub Actions to create and approve pull requests"

## Validation Steps

After configuration, verify:

1. Variables are set correctly:
   - `PYTHON_VERSION`: `3.10`
   - `AWS_REGION`: `us-east-1`

2. Secrets are configured:
   - `GEMINI_API_KEY`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. Environments are properly named:
   - `staging`
   - `production`

4. Environment URLs are set:
   - Staging: https://dev.example.com
   - Production: https://prod.example.com

5. Branch protection rules are active

## Troubleshooting

### Environment Errors
If you see "Value 'X' is not valid" errors:
1. Check environment names match exactly:
   - `staging` (not 'dev' or 'development')
   - `production` (not 'prod')
2. Verify environments are created in repository settings
3. Check environment protection rules

### Variable Access
For variables not being set:
1. Verify variables exist in repository settings
2. Check variable names are exact matches
3. Ensure variables are created at repository level

### Secret Access Warnings
For "Context access might be invalid" warnings:
1. These are linter warnings and can be safely ignored
2. Verify secrets exist in repository settings
3. Check secret names match exactly

### AWS Authentication Issues
1. Verify AWS credentials are correct
2. Test AWS credentials locally:
   ```bash
   aws configure
   aws s3 ls  # Test command
   ```
3. Check CloudWatch logs for access errors
4. Verify AWS region matches configuration
