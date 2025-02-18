# GitHub Environments Setup Guide

This guide explains how to set up the required environments for the Multi-Role Pipeline workflow.

## Required Environments

### 1. Test Environment
```bash
Name: test
URL: https://test.example.com
```

#### Protection Rules
- No required reviewers
- No wait timer
- Allow all branches to deploy

#### Purpose
- Used for running QA tasks
- Automated tests and quality checks
- No manual approval required

### 2. Staging Environment
```bash
Name: staging
URL: https://staging.example.com
```

#### Protection Rules
- No required reviewers
- No wait timer
- Allow all branches to deploy

#### Purpose
- Pre-production testing
- Integration testing
- Feature validation

### 3. Production Environment
```bash
Name: production
URL: https://prod.example.com
```

#### Protection Rules
- Required reviewers: 1
- Wait timer: 10 minutes
- Deployment branches: main only

#### Purpose
- Live production environment
- Requires manual approval
- Protected deployment process

## Setup Instructions

1. **Navigate to Environment Settings**
   ```
   Repository Settings → Environments → New environment
   ```

2. **Create Test Environment**
   - Click "New environment"
   - Name: `test`
   - Configure URL: `https://test.example.com`
   - Skip protection rules
   - Click "Save protection rules"

3. **Create Staging Environment**
   - Click "New environment"
   - Name: `staging`
   - Configure URL: `https://staging.example.com`
   - Skip protection rules
   - Click "Save protection rules"

4. **Create Production Environment**
   - Click "New environment"
   - Name: `production`
   - Configure URL: `https://prod.example.com`
   - Enable "Required reviewers"
   - Add required reviewers
   - Set deployment wait timer: 10 minutes
   - Restrict environment to `main` branch
   - Click "Save protection rules"

## Environment Variables

### Repository Variables
Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**:

1. `PYTHON_VERSION`
   ```
   Name: PYTHON_VERSION
   Value: 3.10
   ```

2. `AWS_REGION`
   ```
   Name: AWS_REGION
   Value: us-east-1
   ```

### Repository Secrets
Go to **Settings** → **Secrets and variables** → **Actions** → **Secrets**:

1. `GEMINI_API_KEY`
   ```
   Name: GEMINI_API_KEY
   Value: [Your Gemini API Key]
   ```

2. `AWS_ACCESS_KEY_ID`
   ```
   Name: AWS_ACCESS_KEY_ID
   Value: [Your AWS Access Key]
   ```

3. `AWS_SECRET_ACCESS_KEY`
   ```
   Name: AWS_SECRET_ACCESS_KEY
   Value: [Your AWS Secret Key]
   ```

## Deployment Flow

1. **QA Stage**
   - Runs in `test` environment
   - No approval required
   - Automated tests and quality checks

2. **Staging Deployment**
   - Deploys to `staging` environment
   - No approval required
   - Integration testing and validation

3. **Production Deployment**
   - Deploys to `production` environment
   - Requires manual approval
   - 10-minute wait period
   - Only deploys from main branch

4. **Production Monitoring**
   - Runs in `production` environment
   - Monitors live deployment
   - Generates performance reports

## Troubleshooting

### Common Issues

1. **Environment Not Found**
   - Verify environment name matches exactly
   - Check for typos in environment names
   - Ensure environment is created in repository settings

2. **Protection Rule Issues**
   - Verify reviewer permissions
   - Check branch restrictions
   - Confirm wait timer settings

3. **URL Configuration**
   - Ensure URLs are properly formatted
   - Verify URLs are accessible
   - Check for HTTPS protocol

4. **Secret Access**
   - Verify secrets are set at repository level
   - Check secret names match workflow
   - Ensure proper access permissions

### Validation Steps

1. **Environment Setup**
   ```bash
   # Check environment exists
   Settings → Environments → [environment name]
   ```

2. **Protection Rules**
   ```bash
   # Verify protection rules
   Settings → Environments → [environment name] → Protection rules
   ```

3. **Secret Access**
   ```bash
   # Test secret access
   Settings → Secrets and variables → Actions → [secret name]
   ```

4. **Variable Access**
   ```bash
   # Verify variables
   Settings → Secrets and variables → Actions → Variables
   ```
