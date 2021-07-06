provider "aws" {
  shared_credentials_file = var.shared_credentials_file
  region                  = "us-east-1"
  profile                 = "ghh"
}

#provider "random_pet" {}

resource "random_pet" "s3" {
  length = 2
}