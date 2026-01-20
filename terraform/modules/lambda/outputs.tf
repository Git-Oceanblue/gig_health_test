output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.backend.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.backend.function_name
}

output "function_url" {
  description = "Function URL for the Lambda function"
  value       = aws_lambda_function_url.backend_url.function_url
}