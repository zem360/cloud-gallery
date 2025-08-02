output "table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.art_gallery.name
}

output "table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.art_gallery.arn
}