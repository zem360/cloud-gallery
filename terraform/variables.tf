variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "cloud-gallery"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "website_bucket_name" {
  description = "Name of the S3 bucket for static website hosting"
  type        = string
}