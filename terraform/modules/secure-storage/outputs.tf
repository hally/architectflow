output "bucket_name" {
  description = "Name of the S3 document bucket."
  value       = aws_s3_bucket.documents.id
}
