resource "aws_iam_role" "step_functions_role" {
  name = "${var.state_machine_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "step_functions_lambda_policy" {
  name = "${var.state_machine_name}-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          var.lambda_fetch_art_arn,
          var.lambda_process_store_arn,
          var.lambda_generate_html_arn,
          var.lambda_notifications_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_lambda_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_lambda_policy.arn
}

resource "aws_sfn_state_machine" "art_pipeline" {
  name     = var.state_machine_name
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "Cloud Gallery Art Pipeline - Daily artwork processing workflow"
    StartAt = "FetchArtworks"
    States = {
      FetchArtworks = {
        Type     = "Task"
        Resource = var.lambda_fetch_art_arn
        Comment  = "Fetch 9 artworks from Art Institute API"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next        = "HandleError"
            ResultPath  = "$.error"
          }
        ]
        Next = "CheckFetchResults"
      }

      CheckFetchResults = {
        Type = "Choice"
        Comment = "Check if artworks were successfully fetched"
        Choices = [
          {
            Variable      = "$.statusCode"
            NumericEquals = 200
            Next          = "ProcessAndStore"
          }
        ]
        Default = "HandleError"
      }

      ProcessAndStore = {
        Type     = "Task"
        Resource = var.lambda_process_store_arn
        Comment  = "Process artwork data and store in DynamoDB"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next        = "HandleError"
            ResultPath  = "$.error"
          }
        ]
        Next = "CheckProcessResults"
      }

      CheckProcessResults = {
        Type = "Choice"
        Comment = "Check if data was successfully stored"
        Choices = [
          {
            Variable      = "$.statusCode"
            NumericEquals = 200
            Next          = "GenerateHTML"
          },
          {
            Variable      = "$.statusCode"
            NumericEquals = 207
            Comment       = "Partial success - continue anyway"
            Next          = "GenerateHTML"
          }
        ]
        Default = "HandleError"
      }

      GenerateHTML = {
        Type     = "Task"
        Resource = var.lambda_generate_html_arn
        Comment  = "Generate HTML gallery and upload to S3"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next        = "HandleError"
            ResultPath  = "$.error"
          }
        ]
        Next = "CheckHTMLResults"
      }

      CheckHTMLResults = {
        Type = "Choice"
        Comment = "Check if HTML was successfully generated"
        Choices = [
          {
            Variable      = "$.statusCode"
            NumericEquals = 200
            Next          = "SendNotifications"
          }
        ]
        Default = "HandleError"
      }

      SendNotifications = {
        Type     = "Task"
        Resource = var.lambda_notifications_arn
        Comment  = "Send completion notifications"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 2
            BackoffRate     = 2.0
          }
        ]
        Next = "Success"
      }

      Success = {
        Type = "Succeed"
        Comment = "Pipeline completed successfully"
      }

      HandleError = {
        Type = "Task"
        Resource = var.lambda_notifications_arn
        Comment = "Handle pipeline errors and send error notifications"
        Parameters = {
          "body.$" = "$.error"
          "pipeline_status" = "FAILED"
        }
        Next = "Failure"
      }

      Failure = {
        Type = "Fail"
        Comment = "Pipeline failed"
      }
    }
  })

  tags = merge(var.tags, {
    Name        = var.state_machine_name
    Environment = var.environment
  })
}