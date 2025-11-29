# Deployment Guide

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [AWS Account Setup](#aws-account-setup)
- [Supabase Database Setup](#supabase-database-setup)
- [Cloudflare R2 Storage Setup](#cloudflare-r2-storage-setup)
- [Terraform Configuration](#terraform-configuration)
- [Backend Deployment (Docker + ECS)](#backend-deployment-docker--ecs)
- [Frontend Deployment](#frontend-deployment)
- [DNS and SSL Configuration](#dns-and-ssl-configuration)
- [Verification](#verification)
- [Monitoring and Logs](#monitoring-and-logs)
- [Updates and Maintenance](#updates-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

### Required Tools

```bash
# AWS CLI
aws --version  # v2+ required

# Terraform
terraform --version  # v1+ required

# Docker
docker --version

# Node.js
node --version  # v20+ required

# Python
python3 --version  # v3.11+ required
```

### Install Tools

```bash
brew install awscli terraform docker node python@3.11
```

### Required Accounts

- AWS Account with admin access
- Supabase account (free tier works)
- Cloudflare account with R2 access
- Brightdata account for JS-heavy sites
- OpenRouter account for LLM enhancement (optionally use AI provider of your choosing)

## AWS Account Setup

### 1. Configure AWS CLI

```bash
aws configure
```

Provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1` (or your preferred region)
- Default output format: `json`

### 2. Verify AWS Access

```bash
aws sts get-caller-identity
```

Should return your AWS account information.

### 3. Get VPC and Subnet Information

The ECS deployment requires a VPC and at least 2 subnets in different availability zones.

**Get Default VPC:**
```bash
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text
```

**Get Subnets:**
```bash
# Replace vpc-xxx with your VPC ID
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-xxx" \
  --query "Subnets[*].[SubnetId,AvailabilityZone]" \
  --output table
```

Select **at least 2 subnets in different availability zones**.

## Supabase Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note down:
   - Project URL: `https://xxx.supabase.co`
   - Anon Key: `xxxxxxxxxxxxxxxxx...`

### 2. Run Database Migration

1. In Supabase dashboard, go to SQL Editor
2. Create new query
3. Paste contents from `backend/migrations/001_create_crawl_sites.sql`:

```sql
CREATE TABLE crawl_sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_url TEXT UNIQUE NOT NULL,
    max_pages INTEGER DEFAULT 50,
    desc_length INTEGER DEFAULT 500,
    recrawl_interval_minutes INTEGER DEFAULT 360,
    last_crawled_at TIMESTAMP WITH TIME ZONE,
    llms_txt_url TEXT,
    llms_txt_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_base_url ON crawl_sites(base_url);
CREATE INDEX idx_next_crawl ON crawl_sites (
    (last_crawled_at + (recrawl_interval_minutes || ' minutes')::INTERVAL)
);
```

4. Run the query
5. Verify table created in Table Editor

## Cloudflare R2 Storage Setup

### 1. Create R2 Bucket

1. Log into Cloudflare dashboard
2. Go to R2 Object Storage
3. Create bucket: `llms-txt`
4. Enable public access for the bucket

### 2. Create API Token

1. In R2, go to "Manage R2 API Tokens"
2. Create API Token with:
   - Permissions: Read & Write
   - Bucket: `llms-txt` (or all buckets)
3. Note down:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (format: `https://xxx.r2.cloudflarestorage.com`)

### 3. Get Public Domain

1. In bucket settings, enable public access
2. Copy the public domain URL (format: `https://pub-xxx.r2.dev`)

## Terraform Configuration

### 1. Copy Example Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

### 2. Edit terraform.tfvars

1. Fill in environment credentials

**Configure all variables:**

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "production"

# Supabase Configuration
supabase_url = "https://xxx.supabase.co"
supabase_key = "your_supabase_anon_key"

# Cloudflare R2 Configuration
r2_endpoint      = "https://xxx.r2.cloudflarestorage.com"
r2_access_key    = "your_r2_access_key"
r2_secret_key    = "your_r2_secret_key"
r2_bucket        = "llms-txt"
r2_public_domain = "https://pub-xxx.r2.dev"

# Optional API Keys
brightdata_api_key      = ""  # Leave empty if not using
openrouter_api_key      = ""  # Leave empty if not using
llm_enhancement_enabled = "false"

# Network Configuration
vpc_id     = "vpc-xxx"  # From AWS setup step
subnet_ids = ["subnet-xxx", "subnet-yyy"]  # At least 2 in different AZs

# Application Configuration
cors_origins = "http://localhost:3000,https://yourdomain.com"
cron_secret  = ""  # Generate below
api_key      = ""  # Generate below
```

### 3. Generate Security Keys

```bash
# Generate API key for WebSocket and cron secret
openssl rand -base64 32
```

Add these values to `terraform.tfvars`:
```hcl
api_key     = "generated_api_key_here"
cron_secret = "generated_cron_secret_here"
```

### 4. Initialize Terraform

```bash
cd terraform
terraform init
```

## Backend Deployment (Docker + ECS)

### 1. Build Lambda Deployment Package

The Lambda function requires dependencies packaged in a zip file.

```bash
cd backend/deployment
./build_lambda.sh
```

This creates `lambda-deployment.zip` with all Python dependencies.

**Verify:**
```bash
ls -lh lambda-deployment.zip
# Should be ~70MB
```

### 2. Copy Lambda Package

```bash
cp backend/deployment/lambda-deployment.zip backend/lambda-deployment.zip
```

### 3. Build Docker Image

```bash
cd backend
docker build -t llmstxt-api .
```

### 4. Apply Terraform Infrastructure

```bash
cd terraform
terraform plan  # Review changes
terraform apply
```

Type `yes` when prompted. This creates:
- ECR repository
- ECS cluster and task definition
- Application Load Balancer
- Security groups
- IAM roles
- Lambda function
- EventBridge schedule
- CloudWatch log groups

**Deployment time: ~5-10 minutes**

### 5. Get ECR Repository URL

```bash
terraform output ecr_repository_url
```

### 6. Push Docker Image to ECR

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <YOUR_URL>

# Tag image
docker tag llmstxt-api:latest \
  <YOUR_URL>

# Push to ECR
docker push <YOUR_URL>/llmstxt-api:latest
```

### 7. Force ECS Service Update

```bash
aws ecs update-service \
  --cluster llmstxt-cluster \
  --service llmstxt-api-service \
  --force-new-deployment \
  --region us-east-1
```

### 8. Wait for Deployment

```bash
aws ecs describe-services \
  --cluster llmstxt-cluster \
  --services llmstxt-api-service \
  --query "services[0].deployments" \
  --region us-east-1

# Watch task status
aws ecs list-tasks \
  --cluster llmstxt-cluster \
  --service-name llmstxt-api-service \
  --region us-east-1
```

Wait until:
- Running count: 1
- Desired count: 1
- Deployment status: PRIMARY

### 9. Get Backend URL

```bash
terraform output alb_dns_name
```

Test backend:
```bash
curl <YOUR_URL>/health
# Response: {"status":"ok"}
```

## Frontend Deployment

### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy frontend:
```bash
cd frontend
vercel --prod
```

3. Add environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_WS_URL`: `wss://your-backend-url/ws/crawl`
   - `NEXT_PUBLIC_API_KEY`: Your generated API key

## DNS and SSL Configuration
```

### ACM Certificate + AWS Route53

1. Request certificate (already created by Terraform):
```bash
terraform output acm_certificate_arn
```

2. Get validation CNAME:
```bash
terraform output acm_certificate_validation_options
```

3. Add CNAME record to your DNS provider

4. Wait for validation (can take up to 30 minutes)

5. Create Route53 alias record pointing to ALB:
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id <your-zone-id> \
  --change-batch file://dns-change.json
```

`dns-change.json`:
```json
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.yourdomain.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "<alb-hosted-zone-id>",
        "DNSName": "llmstxt-alb-xxx.us-east-1.elb.amazonaws.com",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
```

## Verification

### 1. Test Backend Health

```bash
curl https://llmstxt-backend.yourdomain.com/health
# {"status":"ok"}
```

### 2. Test WebSocket Connection

```bash
# Using websocat (install: brew install websocat)
echo '{"url":"https://example.com","maxPages":5,"descLength":200}' | \
  websocat "wss://llmstxt-backend.yourdomain.com/ws/crawl?api_key=YOUR_KEY"
```