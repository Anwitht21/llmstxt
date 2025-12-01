variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Supabase
variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
  sensitive   = true
}

variable "supabase_key" {
  description = "Supabase anon key"
  type        = string
  sensitive   = true
}

# Cloudflare R2
variable "r2_endpoint" {
  description = "Cloudflare R2 endpoint"
  type        = string
  sensitive   = true
}

variable "r2_access_key" {
  description = "Cloudflare R2 access key"
  type        = string
  sensitive   = true
}

variable "r2_secret_key" {
  description = "Cloudflare R2 secret key"
  type        = string
  sensitive   = true
}

variable "r2_bucket" {
  description = "Cloudflare R2 bucket name"
  type        = string
  default     = "llmstxt"
}

variable "r2_public_domain" {
  description = "Cloudflare R2 public domain"
  type        = string
}

# Optional API keys
variable "brightdata_api_key" {
  description = "Brightdata API key (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openrouter_api_key" {
  description = "OpenRouter API key (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "llm_enhancement_enabled" {
  description = "Enable LLM enhancement"
  type        = string
  default     = "false"
}

# Network
variable "vpc_id" {
  description = "VPC ID for ECS and ALB"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks and ALB (must be in different AZs)"
  type        = list(string)
}

# Application
variable "cors_origins" {
  description = "CORS allowed origins"
  type        = string
  default     = "*"
}

variable "cron_secret" {
  description = "Secret token for cron endpoint"
  type        = string
  sensitive   = true
}

variable "api_key" {
  description = "API key for WebSocket authentication"
  type        = string
  sensitive   = true
}

# Frontend
variable "github_repository" {
  description = "GitHub repository URL for Amplify (e.g., https://github.com/username/repo)"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token for Amplify (optional - can be added later via AWS Console)"
  type        = string
  default     = ""
  sensitive   = true
}

# Optional: Domain for Amplify
# variable "domain_name" {
#   description = "Custom domain name for Amplify"
#   type        = string
#   default     = ""
# }

# Optional: HTTPS certificate
# variable "acm_certificate_arn" {
#   description = "ACM certificate ARN for HTTPS"
#   type        = string
#   default     = ""
# }

# Monitoring
variable "alert_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
}
