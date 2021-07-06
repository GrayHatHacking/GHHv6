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
  description = "A list of CIDRs that will be allowed to access the EC2 instances"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "dns_zone" {
    type         = string
    description  = "Kubernetes needs a Route53 DNS Domain, please enter your Route53 Domain"
}

variable "networks" {
  type = map(object({
    cidr_block        = string
    availability_zone = string
  }))
  default = {
    n0 = {
      cidr_block        = "10.0.0.0/24"
      availability_zone = "us-east-1a"
    }
    n1 = {
      cidr_block        = "10.0.1.0/24"
      availability_zone = "us-east-1b"
    }
    n2 = {
      cidr_block        = "10.0.2.0/24"
      availability_zone = "us-east-1c"
    }
  }
}