resource "random_string" "random" {
  length           = 8
  special          = false
  upper            = false
}

variable "aws_region" {
  default = "us-east-1"
}
variable "aws_profile" {
  default = "ghh"
}

variable "shared_credentials_file" {
  description = "Path to your AWS credentials file"
  type        = string
  default     = "/home/kali/.aws/credentials"
}

variable "key_path" {
description = "Key path for SSHing into EC2"
default  = "/home/kali/.ssh/id_rsa"
}

variable "key_name" {
description = "Key name for SSHing into EC2"
default = "ghh"
}

variable "ip_allowlist" {
  description = "A list of CIDRs that will be alowed to access the EC2 instances"
  type        = list(string)
  default     = ["0.0.0.0/0","10.0.0.0/24"]
}

variable "dc_password" {
  default = "GrayHatHack1ng!"
}
