# S3 bucket for frontend_gig hosting
resource "aws_s3_bucket" "frontend_gig" {
  bucket = "resume-auto-frontend_gig-${var.environment}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "frontend_gig" {
  bucket = aws_s3_bucket.frontend_gig.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend_gig" {
  bucket = aws_s3_bucket.frontend_gig.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "frontend_gig" {
  bucket = aws_s3_bucket.frontend_gig.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "frontend_gig" {
  bucket = aws_s3_bucket.frontend_gig.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "frontend_gig" {
  bucket = aws_s3_bucket.frontend_gig.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend_gig.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend_gig]
}