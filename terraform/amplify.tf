# AWS Amplify
resource "aws_amplify_app" "llmstxt_frontend" {
  name         = "llmstxt-frontend"
  repository   = var.github_repository
  access_token = var.github_token != "" ? var.github_token : null

  # Build settings
  build_spec = <<-EOT
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - cd frontend
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: frontend
        files:
          - '.next/**/*'
          - 'public/**/*'
          - 'package.json'
          - 'node_modules/**/*'
      cache:
        paths:
          - frontend/node_modules/**/*
  EOT

  # Environment variables
  environment_variables = {
    NEXT_PUBLIC_WS_URL = "ws://${aws_lb.llmstxt.dns_name}/ws/crawl"
  }

  # Enable auto branch creation
  enable_auto_branch_creation = true
  enable_branch_auto_build    = true

  tags = {
    Name        = "llmstxt-frontend"
    Environment = var.environment
  }
}

# Infra branch
resource "aws_amplify_branch" "infra" {
  app_id      = aws_amplify_app.llmstxt_frontend.id
  branch_name = "infra"

  framework = "Next.js - SSR"
  stage     = "PRODUCTION"

  enable_auto_build = true

  tags = {
    Name        = "llmstxt-frontend-infra"
    Environment = var.environment
  }
}

# Optional: Domain association (uncomment and configure if needed)
# resource "aws_amplify_domain_association" "llmstxt" {
#   app_id      = aws_amplify_app.llmstxt_frontend.id
#   domain_name = var.domain_name
#
#   sub_domain {
#     branch_name = aws_amplify_branch.main.branch_name
#     prefix      = ""
#   }
#
#   sub_domain {
#     branch_name = aws_amplify_branch.main.branch_name
#     prefix      = "www"
#   }
# }
