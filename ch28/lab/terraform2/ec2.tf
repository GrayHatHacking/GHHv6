#Security Groups
resource "aws_security_group" "ghh-ec2-security-group" {
  name = "ghh-ec2-ssh2"
  description = "Security Group for EC2 Instance over SSH"
  vpc_id = aws_vpc.this.id
  ingress {
      from_port = 1234
      to_port = 1234
      protocol = "tcp"
      cidr_blocks = var.ip_allowlist
  }

  ingress {
      from_port = 1234
      to_port = 1234
      protocol = "tcp"
      cidr_blocks = var.ip_allowlist
  }
  
  egress {
      from_port = 0
      to_port = 0
      protocol = "-1"
      cidr_blocks = [
          "0.0.0.0/0"
      ]
  }
  tags = {
    Name = "ghh-ec2-ssh2"
  }
}

#EC2 Instance
resource "aws_instance" "ghh-ubuntu-test" {
    ami                         = data.aws_ami.ubuntu.id
    instance_type               = "t2.micro"
    subnet_id                   = aws_subnet.this.id
    associate_public_ip_address = true
    vpc_security_group_ids      = [aws_security_group.ghh-ec2-security-group.id]
    key_name                    = var.key_name
    private_ip                  = "10.0.0.30"

    root_block_device {
        volume_type = "gp2"
        volume_size = 8
        delete_on_termination = true
    }
    volume_tags = {
        Name = "EC2 Instance Root Device"
    }
    user_data = <<-EOF
        #!/bin/bash
        curl -U monitoring:monitoring http://localhost/_healthz
        EOF
    tags = {
        Name = "ghh-ubuntu-ec2"
    }
}
