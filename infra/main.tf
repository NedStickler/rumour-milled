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

# ECR Scraper Repo
resource "aws_ecr_repository" "scraper_repo" {
  count = vars.env != "local" ? 1 : 0
  name = "rumour-milled/rm-${var.env}-scraper-repo"
}

# ECR Finish Handler Repo
resource "aws_ecr_repository" "scraper_finish_handler_repo" {
  count = vars.env != "local" ? 1 : 0
  name = "rumour-milled/rm-${var.env}-scrape-finish-handler-repo"
}

