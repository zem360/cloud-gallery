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

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "lambda_fetch_art_name" {
  description = "Name of the fetch art Lambda function"
  type        = string
}

variable "lambda_process_store_name" {
  description = "Name of the process and store Lambda function"
  type        = string
}

variable "lambda_generate_html_name" {
  description = "Name of the generate HTML Lambda function"
  type        = string
}

variable "lambda_notifications_name" {
  description = "Name of the notifications Lambda function"
  type        = string
}

variable "step_functions_name" {
  description = "Name of the Step Functions state machine"
  type        = string
}

variable "eventbridge_rule_name" {
  description = "Name of the EventBridge rule"
  type        = string
}

variable "schedule_expression" {
  description = "Cron expression for daily schedule"
  type        = string
  default     = "cron(0 12 * * ? *)"  # Daily at 12:00 PM UTC
}