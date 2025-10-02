# S3
resource "aws_s3_bucket" "training_bucket" {
  bucket = "rm-${var.env}-training-bucket"
}

# DynamoDB
resource "aws_dynamodb_table" "headlines_db" {
  name           = "rm-${var.env}-headlines-table"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10
  hash_key       = "headline"
  range_key      = "timestamp"

  attribute {
    name = "headline"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }
}

# ECR
resource "aws_ecr_repository" "scraper_repo" {
  name = "rumour-milled/rm-${var.env}-scraper"
}