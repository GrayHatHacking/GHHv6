data "aws_availability_zones" "this" {
  state = "available"
}

data "aws_ami" "ghh-kali" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ghh-kali-*"]
  }


  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["self"] 
}

