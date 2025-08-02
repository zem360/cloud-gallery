resource "aws_dynamodb_table" "art_gallery" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"  
  hash_key       = "artwork_id"
  
  attribute {
    name = "artwork_id"
    type = "S"
  }
  
  attribute {
    name = "date_fetched"
    type = "S"
  }

  global_secondary_index {
    name     = "DateIndex"
    hash_key = "date_fetched"
    projection_type = "ALL"
  }

  tags = merge(var.tags, {
    Name        = var.table_name
    Environment = var.environment
    Purpose     = "Art Gallery Data Storage"
  })
}