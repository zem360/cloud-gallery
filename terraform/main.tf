# S3 module for website hosting
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