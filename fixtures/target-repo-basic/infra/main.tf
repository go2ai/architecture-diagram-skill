resource "aws_sqs_queue" "orders" {
  name = "orders-queue"
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "orders-artifacts"
}

resource "aws_db_instance" "orders" {
  identifier = "orders-db"
}
