# Lambda outputs
output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.llmstxt_auto_update.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.llmstxt_auto_update.function_name
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.recrawl_schedule.arn
}

output "cloudwatch_log_group_lambda" {
  description = "CloudWatch log group name for Lambda"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

# ECS outputs
output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.llmstxt_api.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.llmstxt.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.llmstxt_api.name
}

output "cloudwatch_log_group_ecs" {
  description = "CloudWatch log group name for ECS"
  value       = aws_cloudwatch_log_group.ecs_logs.name
}

# ALB outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.llmstxt.dns_name
}

output "alb_url" {
  description = "Full URL of the backend API"
  value       = "http://${aws_lb.llmstxt.dns_name}"
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.llmstxt.arn
}

# Amplify outputs
output "amplify_app_id" {
  description = "Amplify App ID"
  value       = aws_amplify_app.llmstxt_frontend.id
}

output "amplify_default_domain" {
  description = "Default domain for Amplify app"
  value       = aws_amplify_app.llmstxt_frontend.default_domain
}

output "amplify_app_url" {
  description = "Full URL of the frontend application"
  value       = "https://infra.${aws_amplify_app.llmstxt_frontend.default_domain}"
}
