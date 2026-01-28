output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.frontend_gig.id
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.frontend_gig.bucket
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.frontend_gig.bucket_domain_name
}

output "bucket_website_endpoint" {
  description = "Website endpoint of the S3 bucket"
  value       = aws_s3_bucket_website_configuration.frontend_gig.website_endpoint
}
