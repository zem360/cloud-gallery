output "rule_name" {
  description = "Name of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.daily_schedule.name
}

output "rule_arn" {
  description = "ARN of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.daily_schedule.arn
}

output "schedule_expression" {
  description = "Schedule expression for the rule"
  value       = aws_cloudwatch_event_rule.daily_schedule.schedule_expression
}