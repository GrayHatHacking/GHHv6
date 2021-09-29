
locals {
  dc-userdata = <<EOF
<powershell>
  $admin = [adsi]("WinNT://./administrator, user")
  $admin.psbase.invoke("SetPassword", "${var.dc_password}")
</powershell>

EOF
}


resource "aws_instance" "kali" {
  ami           = data.aws_ami.ghh-kali.id
  instance_type = "t2.large"
  key_name = var.key_name

  subnet_id = aws_subnet.this.id

  vpc_security_group_ids = [aws_security_group.allow-ssh.id]
  associate_public_ip_address = true
  private_ip = "10.0.0.40"

  root_block_device {
        volume_size = 200 
  }



  tags = {
    Name = "ghh-kali"
  }
}

resource "aws_instance" "ghh_dc" {
  ami           = data.aws_ami.ghh-2019.id
  instance_type = "t2.large"


  key_name = var.key_name

  subnet_id = aws_subnet.this.id

  private_ip = "10.0.0.10"
  user_data_base64 = base64encode(local.dc-userdata)
  vpc_security_group_ids = [aws_security_group.ghh_windows.id]
  associate_public_ip_address = true
  get_password_data = "true"


  root_block_device {
        volume_size = 200 
  }



  tags = {
    Name = "ghh-dc"
  }
}


resource "aws_instance" "ghh_target" {
  ami           = data.aws_ami.ghh-2016.id
  instance_type = "t2.large"


  key_name = var.key_name

  subnet_id = aws_subnet.this.id
  private_ip = "10.0.0.20"
  user_data_base64 = base64encode(local.dc-userdata)

  vpc_security_group_ids = [aws_security_group.ghh_windows.id]
  associate_public_ip_address = true
  get_password_data = "true"


  root_block_device {
        volume_size = 200 
  }



  tags = {
    Name = "ghh-target"
  }
}


resource "aws_instance" "ghh_util" {
  ami           = data.aws_ami.ghh-2016.id
  instance_type = "t2.large"


  key_name = var.key_name

  subnet_id = aws_subnet.this.id

  vpc_security_group_ids = [aws_security_group.ghh_windows.id]
  associate_public_ip_address = true
  get_password_data = "true"
  private_ip = "10.0.0.30"
  user_data_base64 = base64encode(local.dc-userdata)


  root_block_device {
        volume_size = 200 
  }



  tags = {
    Name = "ghh-target"
  }
}
