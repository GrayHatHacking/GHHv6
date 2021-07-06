resource "aws_instance" "kali" {
  ami           = data.aws_ami.ghh-kali.id
  instance_type = "t2.large"
  key_name = var.key_name

  subnet_id = aws_subnet.subnets.0.id
  
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
