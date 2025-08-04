resource "aws_iam_role" "eventbridge_role" {
  name = "${var.rule_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "eventbridge_stepfunctions_policy" {
  name = "${var.rule_name}-stepfunctions-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution",
          "states:StopExecution"
        ]
        Resource = var.step_function_arn
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "eventbridge_stepfunctions_attach" {
  role       = aws_iam_role.eventbridge_role.name
  policy_arn = aws_iam_policy.eventbridge_stepfunctions_policy.arn
}

resource "aws_cloudwatch_event_rule" "daily_schedule" {
  name                = var.rule_name
  description         = "Trigger Cloud Gallery art pipeline daily"
  schedule_expression = var.schedule_expression
  state               = "ENABLED"

  tags = merge(var.tags, {
    Name        = var.rule_name
    Environment = var.environment
  })
}

resource "aws_cloudwatch_event_target" "step_function_target" {
  rule      = aws_cloudwatch_event_rule.daily_schedule.name
  target_id = "CloudGalleryPipelineTarget"
  arn       = var.step_function_arn
  role_arn  = aws_iam_role.eventbridge_role.arn

  input = jsonencode({
    comment = "Daily execution triggered by EventBridge"
    source  = "eventbridge.daily.schedule"
  })

  depends_on = [
    aws_iam_role_policy_attachment.eventbridge_stepfunctions_attach
  ]
}