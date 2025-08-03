variable "rule_name" {
  description = "Name of the EventBridge rule"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "schedule_expression" {
  description = "Cron or rate expression for scheduling"
  type        = string
  default     = "cron(0 12 * * ? *)"  # Daily at 12:00 PM UTC
}

variable "step_function_arn" {
  description = "ARN of the Step Functions state machine to trigger"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}