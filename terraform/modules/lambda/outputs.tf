output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.backend_gig.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.backend_gig.function_name
}

output "function_url" {
  description = "Function URL for the Lambda function"
  value       = aws_lambda_function_url.backend_gig_url.function_url
}