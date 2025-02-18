# AWS IAM Configuration for GitHub Actions

This document outlines the required AWS IAM configuration for secure GitHub Actions integration using OpenID Connect (OIDC).

## OIDC Provider Setup

Create the OIDC provider in AWS IAM:

```terraform
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}
```

## IAM Role Configuration

### Role Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:${GITHUB_ORG}/${REPO_NAME}:environment:dev",
            "repo:${GITHUB_ORG}/${REPO_NAME}:environment:prod"
          ]
        }
      }
    }
  ]
}
```

### Role Permissions Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${DEPLOYMENT_BUCKET}",
        "arn:aws:s3:::${DEPLOYMENT_BUCKET}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## GitHub Repository Configuration

1. Create environments in GitHub repository settings:
   - Name: `dev`
   - Name: `prod`

2. Add required secrets:
   - `VITE_GEMINI_API_KEY`: API key for Gemini AI model
   - `AWS_ROLE_ARN`: ARN of the IAM role for GitHub Actions

## Environment Protection Rules

### Dev Environment
- Required reviewers: None
- Wait timer: None
- Deployment branches: All

### Prod Environment
- Required reviewers: 1
- Wait timer: 10 minutes
- Deployment branches: `main` only

## Security Best Practices

1. Use environment-specific roles when possible
2. Implement least-privilege permissions
3. Enable branch protection rules
4. Regular rotation of deployment secrets
5. Monitor AWS CloudTrail for OIDC federation events
