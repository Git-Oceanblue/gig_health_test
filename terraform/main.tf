terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "resumes-gig-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-2"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "resume-gig"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 bucket for frontend (changed the resume-auto-frontend)
module "s3_frontend" {
  source = "./modules/s3"
  
  bucket_name = "gig-frontend-${var.environment}-${data.aws_caller_identity.current.account_id}"
  environment = var.environment
}

# CloudFront distribution
module "cloudfront" {
  source = "./modules/cloudfront"
  
  s3_bucket_id = module.s3_frontend.bucket_id
  s3_bucket_domain_name = module.s3_frontend.bucket_domain_name
  environment = var.environment
}

# Lambda function for backend (changed the resume-auto-backend)
module "lambda" {
  source = "./modules/lambda"
  
  function_name = "gig-backend-${var.environment}"
  environment   = var.environment
  lambda_zip_path = var.lambda_zip_path
  openai_api_key  = var.openai_api_key
}