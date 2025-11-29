# ACM Certificate for ALB HTTPS
resource "aws_acm_certificate" "llmstxt_backend" {
  domain_name       = "llmstxt-backend.leap-cc.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "llmstxt-backend-cert"
    Environment = var.environment
  }
}

# Output the DNS validation records
output "acm_certificate_validation_options" {
  description = "DNS records needed for ACM certificate validation"
  value = [
    for dvo in aws_acm_certificate.llmstxt_backend.domain_validation_options : {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
    }
  ]
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.llmstxt_backend.arn
}
