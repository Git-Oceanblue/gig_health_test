variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, prod, test)"
  type        = string
  validation {
    condition     = contains(["dev", "prod", "test"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod' or 'test'."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "resume-auto"
}

variable "lambda_zip_path" {
  description = "Local path to the packaged Lambda zip (built by CI)"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key for the backend"
  type        = string
  sensitive   = true
}