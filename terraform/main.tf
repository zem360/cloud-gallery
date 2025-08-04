module "s3_website" {
  source = "./modules/s3"
  
  bucket_name = var.website_bucket_name
  environment = var.environment
  
  tags = {
    Component = "Website"
  }
}

module "dynamodb" {
  source = "./modules/dynamodb"
  
  table_name  = var.dynamodb_table_name
  environment = var.environment
  
  tags = {
    Component = "Database"
  }
}

module "lambda_fetch_art" {
  source = "./modules/lambda"
  
  function_name = var.lambda_fetch_art_name
  environment   = var.environment
  source_dir    = "../src/lambda_functions/fetch_art"
  timeout       = 30
  
  tags = {
    Component = "DataFetcher"
  }
}

module "lambda_process_store" {
  source = "./modules/lambda"
  
  function_name = var.lambda_process_store_name
  environment   = var.environment
  source_dir    = "../src/lambda_functions/process_store"
  timeout       = 60
  
  environment_variables = {
    DYNAMODB_TABLE_NAME = module.dynamodb.table_name
  }
  
  tags = {
    Component = "DataProcessor"
  }
}

resource "aws_iam_policy" "dynamodb_access" {
  name = "cloud-gallery-dynamodb-access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = module.dynamodb.table_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_process_store_dynamodb" {
  role       = module.lambda_process_store.role_name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

module "lambda_generate_html" {
  source = "./modules/lambda"
  
  function_name = var.lambda_generate_html_name
  environment   = var.environment
  source_dir    = "../src/lambda_functions/generate_html"
  timeout       = 60
  
  environment_variables = {
    S3_BUCKET_NAME      = module.s3_website.bucket_name
    DYNAMODB_TABLE_NAME = module.dynamodb.table_name
  }
  
  tags = {
    Component = "HTMLGenerator"
  }
}

resource "aws_iam_policy" "s3_access" {
  name = "cloud-gallery-s3-access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Resource = "${module.s3_website.bucket_arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_generate_html_s3" {
  role       = module.lambda_generate_html.role_name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_generate_html_dynamodb" {
  role       = module.lambda_generate_html.role_name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

module "lambda_notifications" {
  source = "./modules/lambda"
  
  function_name = var.lambda_notifications_name
  environment   = var.environment
  source_dir    = "../src/lambda_functions/notifications"
  timeout       = 30
  
  tags = {
    Component = "Notifications"
  }
}

module "step_functions" {
  source = "./modules/step_functions"
  
  state_machine_name         = var.step_functions_name
  environment               = var.environment
  lambda_fetch_art_arn      = module.lambda_fetch_art.function_arn
  lambda_process_store_arn  = module.lambda_process_store.function_arn
  lambda_generate_html_arn  = module.lambda_generate_html.function_arn
  lambda_notifications_arn  = module.lambda_notifications.function_arn
  
  tags = {
    Component = "Orchestration"
  }
}

module "eventbridge" {
  source = "./modules/eventbridge"
  
  rule_name           = var.eventbridge_rule_name
  environment         = var.environment
  schedule_expression = var.schedule_expression
  step_function_arn   = module.step_functions.state_machine_arn
  
  tags = {
    Component = "Scheduler"
  }
}