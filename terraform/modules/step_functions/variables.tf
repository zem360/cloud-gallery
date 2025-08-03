variable "state_machine_name" {
  description = "Name of the Step Functions state machine"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "lambda_fetch_art_arn" {
  description = "ARN of the fetch art Lambda function"
  type        = string
}

variable "lambda_process_store_arn" {
  description = "ARN of the process store Lambda function"
  type        = string
}

variable "lambda_generate_html_arn" {
  description = "ARN of the generate HTML Lambda function"
  type        = string
}

variable "lambda_notifications_arn" {
  description = "ARN of the notifications Lambda function"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}