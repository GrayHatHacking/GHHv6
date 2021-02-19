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
data "aws_ami" "ghh-2019" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ghh-server2019-*"]
  }


  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["self"] 
}
data "aws_ami" "ghh-2016" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ghh-server2016-*"]
  }


  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["self"] 
}
