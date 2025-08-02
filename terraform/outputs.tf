output "website_url" {
  description = "URL of the static website"
  value       = module.s3_website.website_url
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.s3_website.bucket_name
}