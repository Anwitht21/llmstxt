terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for Lambda deployment packages
resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "llmstxt-lambda-deployments-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "llmstxt-lambda-deployments"
    Environment = var.environment
  }
}

# Upload Lambda deployment package to S3
resource "aws_s3_object" "lambda_package" {
  bucket = aws_s3_bucket.lambda_deployments.id
  key    = "lambda-deployment.zip"
  source = "${path.module}/../backend/lambda-deployment.zip"
  etag   = filemd5("${path.module}/../backend/lambda-deployment.zip")

  tags = {
    Name        = "llmstxt-lambda-package"
    Environment = var.environment
  }
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Lambda function
resource "aws_lambda_function" "llmstxt_auto_update" {
  s3_bucket        = aws_s3_bucket.lambda_deployments.id
  s3_key           = aws_s3_object.lambda_package.key
  function_name    = "llmstxt-auto-update"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "lambda_handler.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda-deployment.zip")
  runtime         = "python3.11"
  timeout         = 600  # 10 minutes
  memory_size     = 512

  environment {
    variables = {
      API_URL                  = "https://llmstxt-backend.leap-cc.com"
      CRON_SECRET              = var.cron_secret
    }
  }

  tags = {
    Name        = "llmstxt-auto-update"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.llmstxt_auto_update.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "llmstxt-lambda-logs"
    Environment = var.environment
  }
}

# EventBridge Rule (cron schedule)
resource "aws_cloudwatch_event_rule" "recrawl_schedule" {
  name                = "llmstxt-recrawl-schedule"
  description         = "Trigger llmstxt auto-update every 6 hours"
  schedule_expression = "cron(0 */6 * * ? *)"

  tags = {
    Name        = "llmstxt-recrawl-schedule"
    Environment = var.environment
  }
}

# EventBridge Target (Lambda)
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.recrawl_schedule.name
  target_id = "llmstxt-lambda-target"
  arn       = aws_lambda_function.llmstxt_auto_update.arn
}

# Grant EventBridge permission to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.llmstxt_auto_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.recrawl_schedule.arn
}
