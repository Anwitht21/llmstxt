# ECR Repo
resource "aws_ecr_repository" "llmstxt_api" {
  name                 = "llmstxt-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "llmstxt-api"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "llmstxt" {
  name = "llmstxt-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "llmstxt-cluster"
    Environment = var.environment
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "llmstxt_api" {
  family                   = "llmstxt-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"  # 0.5 vCPU
  memory                   = "1024" # 1 GB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "llmstxt-api"
    image     = "${aws_ecr_repository.llmstxt_api.repository_url}:latest"
    essential = true

    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "SUPABASE_URL", value = var.supabase_url },
      { name = "SUPABASE_KEY", value = var.supabase_key },
      { name = "R2_ENDPOINT", value = var.r2_endpoint },
      { name = "R2_ACCESS_KEY", value = var.r2_access_key },
      { name = "R2_SECRET_KEY", value = var.r2_secret_key },
      { name = "R2_BUCKET", value = var.r2_bucket },
      { name = "R2_PUBLIC_DOMAIN", value = var.r2_public_domain },
      { name = "BRIGHTDATA_API_KEY", value = var.brightdata_api_key },
      { name = "OPENROUTER_API_KEY", value = var.openrouter_api_key },
      { name = "LLM_ENHANCEMENT_ENABLED", value = var.llm_enhancement_enabled },
      { name = "CORS_ORIGINS", value = var.cors_origins },
      { name = "CRON_SECRET", value = var.cron_secret }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    # Health check temporarily disabled - relying on ALB health check only
    # Will re-enable once curl is verified in container
    # healthCheck = {
    #   command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
    #   interval    = 30
    #   timeout     = 5
    #   retries     = 3
    #   startPeriod = 60
    # }
  }])

  tags = {
    Name        = "llmstxt-api"
    Environment = var.environment
  }
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/llmstxt-api"
  retention_in_days = 14

  tags = {
    Name        = "llmstxt-ecs-logs"
    Environment = var.environment
  }
}

# ECS Service
resource "aws_ecs_service" "llmstxt_api" {
  name            = "llmstxt-api-service"
  cluster         = aws_ecs_cluster.llmstxt.id
  task_definition = aws_ecs_task_definition.llmstxt_api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.llmstxt_api.arn
    container_name   = "llmstxt-api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name        = "llmstxt-api-service"
    Environment = var.environment
  }
}
