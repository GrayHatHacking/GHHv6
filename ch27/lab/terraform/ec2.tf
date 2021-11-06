locals {
  dc-userdata = <<EOF
<powershell>
  $admin = [adsi]("WinNT://./administrator, user")
  $admin.psbase.invoke("SetPassword", "${var.dc_password}")
</powershell>

EOF
}

#Security Groups
resource "aws_security_group" "ghh-ec2-security-group" {
  name = "ghh-ec2-ssh"
  description = "Security Group for EC2 Instance over SSH"
  vpc_id = aws_vpc.this.id
  ingress {
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = var.ip_allowlist
  }

  ingress {
      from_port = 80
      to_port = 80
      protocol = "tcp"
      cidr_blocks = var.ip_allowlist
  }

  ingress {
      from_port = 8080
      to_port = 8080
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
    Name = "ghh-ec2-ssh"
  }
}

resource "aws_security_group" "ghh_windows" {
  vpc_id      = aws_vpc.this.id
  name        = "ghh_windows"
  description = "security group that allows windows ports"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["224.0.0.0/24"]
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  ingress {
    from_port   = 5985
    to_port     = 5986
    protocol    = "tcp"
    cidr_blocks = var.ip_allowlist
  }

  tags = {
    Name = "ghh-rules"
  }
}

#EC2 Instance
resource "aws_instance" "ghh-ubuntu-ec2" {
    ami                         = data.aws_ami.ubuntu.id
    instance_type               = "t2.micro"
    iam_instance_profile        = aws_iam_instance_profile.ghh-ec2-instance-profile.name
    subnet_id                   = aws_subnet.this.id
    associate_public_ip_address = true
    vpc_security_group_ids      = [aws_security_group.ghh-ec2-security-group.id]
    key_name                    = var.key_name
    private_ip                  = "10.0.0.20"

    root_block_device {
        volume_type = "gp2"
        volume_size = 8
        delete_on_termination = true
    }
    provisioner "file" {
      source = "../apps/webapp/index.js"
      destination = "/home/ubuntu/index.js"
      connection {
        type = "ssh"
        user = "ubuntu"
        private_key = file("/home/kali/.ssh/id_rsa")
        host = self.public_ip
      }
    }
    user_data = <<-EOF
        #!/bin/bash
        apt-get update
        curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
        DEBIAN_FRONTEND=noninteractive apt-get -y install nodejs
        npm install http express needle command-line-args
        cd /home/ubuntu
        sudo node index.js &
        echo -e "\n* * * * * root node /home/ubuntu/index.js &\n* * * * * root sleep 10; node /home/ubuntu/index.js &\n* * * * * root sleep 20; node /home/ubuntu/index.js &\n* * * * * root sleep 30; node /home/ubuntu/index.js &\n* * * * * root sleep 40; node /home/ubuntu/index.js &\n* * * * * root sleep 50; node /home/ubuntu/index.js &\n" >> /etc/crontab
        curl -U monitoring:monitoring http://localhost/_healthz
        EOF
    volume_tags = {
        Name = "EC2 Instance Root Device"
    }
    tags = {
        Name = "ghh-ubuntu-ec2"
    }
}

resource "aws_instance" "kali" {
  ami           = data.aws_ami.ghh-kali.id
  instance_type = "t2.large"
  key_name = var.key_name

  subnet_id = aws_subnet.this.id

  vpc_security_group_ids = [aws_security_group.ghh-ec2-security-group.id]
  associate_public_ip_address = true
  private_ip = "10.0.0.40"

  root_block_device {
        volume_size = 200 
  }

  tags = {
    Name = "ghh-kali"
  }
}

resource "aws_instance" "ghh_windows" {
  ami           = data.aws_ami.ghh-2019.id
  instance_type = "t2.medium"


  key_name = var.key_name

  subnet_id = aws_subnet.this.id

  private_ip = "10.0.0.10"
  user_data_base64 = base64encode(local.dc-userdata)
  vpc_security_group_ids = [aws_security_group.ghh_windows.id]
  associate_public_ip_address = true
  get_password_data = "true"


  root_block_device {
        volume_size = 100 
  }

  tags = {
    Name = "ghh-dc"
  }
}
