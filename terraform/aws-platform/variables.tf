variable "aws_region" {
  description = "AWS region for the platform."
  type        = string
  default     = "ca-central-1"
}

variable "environment" {
  type    = string
  default = "development"
}

variable "name_prefix" {
  type    = string
  default = "architectflow"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,20}$", var.name_prefix))
    error_message = "Use 2-21 lowercase letters, numbers or hyphens, starting with a letter."
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "image_tag" {
  description = "Existing image tag in the ECR repository. Push an image before enabling the service."
  type        = string
  default     = "v1"
}

variable "desired_count" {
  description = "Keep at 1 while using SQLite on EFS. 0 avoids starting an ECS task until the image is ready."
  type        = number
  default     = 0
  validation {
    condition     = var.desired_count >= 0 && var.desired_count <= 1
    error_message = "MVP supports zero or one task only (SQLite database)."
  }
}

variable "flask_secret_arn" {
  description = "ARN of an existing Secrets Manager secret holding the Flask SECRET_KEY. Required when desired_count=1."
  type        = string
  default     = ""
}

variable "bedrock_model_arns" {
  description = "Optional exact Bedrock foundation-model or inference-profile ARNs allowed for runtime inference."
  type        = list(string)
  default     = []
}

variable "alert_email" {
  description = "Optional email for AWS Budgets alert; leave empty to skip a budget resource."
  type        = string
  default     = ""
}

variable "monthly_budget_usd" {
  type    = number
  default = 35
}


variable "acm_certificate_arn" {
  description = "ARN of an existing ACM certificate for HTTPS on the load balancer."
  type        = string
  default     = ""
}


variable "enable_private_endpoints" {
  description = "Create private AWS service endpoints (billable). Required when ECS tasks run."
  type        = bool
  default     = false
}
