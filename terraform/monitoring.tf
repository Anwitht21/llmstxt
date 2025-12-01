# SNS Topic for Alerts
resource "aws_sns_topic" "llmstxt_alerts" {
  name = "llmstxt-alerts"

  tags = {
    Name        = "llmstxt-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.llmstxt_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# 1. ECS No Running Tasks
resource "aws_cloudwatch_metric_alarm" "ecs_no_running_tasks" {
  alarm_name          = "llmstxt-ecs-no-running-tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "SampleCount"
  threshold           = "1"
  alarm_description   = "ECS service has no running tasks"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]

  dimensions = {
    ServiceName = aws_ecs_service.llmstxt_api.name
    ClusterName = aws_ecs_cluster.llmstxt.name
  }

  tags = {
    Name        = "llmstxt-ecs-no-running-tasks"
    Environment = var.environment
  }
}

# 2. ALB Unhealthy Targets
resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_targets" {
  alarm_name          = "llmstxt-alb-unhealthy-targets"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "ALB has unhealthy targets"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]

  dimensions = {
    TargetGroup  = aws_lb_target_group.llmstxt_api.arn_suffix
    LoadBalancer = aws_lb.llmstxt.arn_suffix
  }

  tags = {
    Name        = "llmstxt-alb-unhealthy-targets"
    Environment = var.environment
  }
}

# 3. ALB High 5xx Errors
resource "aws_cloudwatch_metric_alarm" "alb_high_5xx_errors" {
  alarm_name          = "llmstxt-alb-high-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "More than 10 5xx errors in 5 minutes"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.llmstxt.arn_suffix
  }

  tags = {
    Name        = "llmstxt-alb-high-5xx-errors"
    Environment = var.environment
  }
}

# 4. Lambda Errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "llmstxt-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Lambda function errors detected"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.llmstxt_auto_update.function_name
  }

  tags = {
    Name        = "llmstxt-lambda-errors"
    Environment = var.environment
  }
}

# 5. Application Error Log Filter
resource "aws_cloudwatch_log_metric_filter" "ecs_application_errors" {
  name           = "llmstxt-ecs-application-errors"
  log_group_name = aws_cloudwatch_log_group.ecs_logs.name
  pattern        = "[ERROR]"

  metric_transformation {
    name          = "ApplicationErrors"
    namespace     = "LLMsTxt/Application"
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "llmstxt-application-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApplicationErrors"
  namespace           = "LLMsTxt/Application"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "More than 5 application errors in 5 minutes"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "llmstxt-application-errors"
    Environment = var.environment
  }
}

# 6. ECS High CPU
resource "aws_cloudwatch_metric_alarm" "ecs_high_cpu" {
  alarm_name          = "llmstxt-ecs-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "ECS CPU utilization > 80% for 15 minutes"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]

  dimensions = {
    ServiceName = aws_ecs_service.llmstxt_api.name
    ClusterName = aws_ecs_cluster.llmstxt.name
  }

  tags = {
    Name        = "llmstxt-ecs-high-cpu"
    Environment = var.environment
  }
}

# 7. ECS High Memory
resource "aws_cloudwatch_metric_alarm" "ecs_high_memory" {
  alarm_name          = "llmstxt-ecs-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "ECS memory utilization > 85% for 15 minutes"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]

  dimensions = {
    ServiceName = aws_ecs_service.llmstxt_api.name
    ClusterName = aws_ecs_cluster.llmstxt.name
  }

  tags = {
    Name        = "llmstxt-ecs-high-memory"
    Environment = var.environment
  }
}

# 8. ALB High Response Time
resource "aws_cloudwatch_metric_alarm" "alb_high_response_time" {
  alarm_name          = "llmstxt-alb-high-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "ALB response time > 5 seconds for 10 minutes"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.llmstxt.arn_suffix
  }

  tags = {
    Name        = "llmstxt-alb-high-response-time"
    Environment = var.environment
  }
}

# 9. Lambda Duration Near Timeout
resource "aws_cloudwatch_metric_alarm" "lambda_duration_high" {
  alarm_name          = "llmstxt-lambda-duration-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "540000"  # 9 minutes (90% of 10min timeout)
  alarm_description   = "Lambda duration > 9 minutes (near timeout)"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.llmstxt_auto_update.function_name
  }

  tags = {
    Name        = "llmstxt-lambda-duration-high"
    Environment = var.environment
  }
}

# 10. Lambda Throttles
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "llmstxt-lambda-throttles"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Lambda function throttled"
  alarm_actions       = [aws_sns_topic.llmstxt_alerts.arn]
  ok_actions          = [aws_sns_topic.llmstxt_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.llmstxt_auto_update.function_name
  }

  tags = {
    Name        = "llmstxt-lambda-throttles"
    Environment = var.environment
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "llmstxt" {
  dashboard_name = "llmstxt-overview"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average", label = "CPU %" }],
            [".", "MemoryUtilization", { stat = "Average", label = "Memory %" }]
          ]
          period = 300
          region = var.aws_region
          title = "ECS Service - CPU & Memory"
          yAxis = { left = { min = 0, max = 100 } }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", { stat = "Sum", label = "Requests" }],
            [".", "HTTPCode_Target_5XX_Count", { stat = "Sum", label = "5xx Errors" }],
            [".", "HTTPCode_Target_2XX_Count", { stat = "Sum", label = "2xx Success" }]
          ]
          period = 300
          region = var.aws_region
          title = "ALB - Requests & Errors"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 6
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Invocations" }],
            [".", "Errors", { stat = "Sum", label = "Errors" }]
          ]
          period = 3600
          region = var.aws_region
          title = "Lambda - Invocations & Errors"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 6
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", { stat = "Average", label = "Avg Duration" }],
            ["...", { stat = "Maximum", label = "Max Duration" }]
          ]
          period = 3600
          region = var.aws_region
          title = "Lambda - Duration (ms)"
        }
      }
    ]
  })
}
