variable "aws_region" {
  default = "us-east-1"
}
variable "aws_profile" {
  default = "ghh"
}
variable "dc_password" {
  default = "GrayHatHack1ng!"
}


variable "shared_credentials_file" {
  description = "Path to your AWS credentials file"
  type        = string
  default     = "/home/username/.aws/credentials"
}

variable "key_path" {
description = "Key path for SSHing into EC2"
default  = "~/.ssh/id_rsa.pem"
}

variable "key_name" {
description = "Key name for SSHing into EC2"
default = "ghh"
}
