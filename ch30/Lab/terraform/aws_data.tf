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

data "aws_ami" "ubuntu" {
  most_recent = true
  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
  
  filter {
      name   = "virtualization-type"
      values = ["hvm"]
  }
}
