#Secret S3 Bucket
resource "aws_s3_bucket" "ghh-secret-bucket" {
  bucket = "ghh-s3-bucket-${random_string.random.id}"
  acl = "private"
  force_destroy = true
  tags = {
      Name = "ghh-secret-bucket"
      Description = "This Buckets for Secrets only"
  }
}

resource "aws_s3_bucket" "ghh-sam-bucket" {
  bucket = "ghh-sam-bucket-${random_string.random.id}"
  acl = "private"
  force_destroy = true
  tags = {
      Name = "ghh-sam-bucket"
      Description = "This Buckets for Secrets only"
  }
}

#resource "aws_s3_bucket_object" "ghh-secret-creds" {
#  bucket = "${aws_s3_bucket.ghh-secret-bucket.id}"
#  key = "secret.txt"
#  source = "../assets/admin-user.txt"
#  tags = {
#    Name = "ghh-secret-data-${random_string.random.id}"
#  }
#}
