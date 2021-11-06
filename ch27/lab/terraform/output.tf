output "random_string" { 
  value =  random_string.random.id 
}

output "victim1" {
  value = try(aws_instance.ghh-ubuntu-ec2.public_ip,null)
}

output "s3_sam_bucket" {
  value = aws_s3_bucket.ghh-sam-bucket.id 
}

output "aws_vpc" {
  value = aws_vpc.this.id
}

output "aws_subnet" {
  value = aws_subnet.this.id
}

output "aws_security_group" {
  value = aws_security_group.ghh-ec2-security-group.id
}

resource "local_file" "kali_inv" {
  content = templatefile("./inventory.tmpl",
  {
    cat = "kali",
    ip_addrs = [aws_instance.kali.public_ip]
    vars = [
      "ansible_user: kali",
      "ansible_python_interpreter: /usr/bin/python3",
      "ansible_ssh_private_key_file: /home/kali/.ssh/id_rsa"
      ]
  }
  )
  filename = "../ansible/inventory/kali.yml"
}

resource "local_file" "victim1" {
  content = templatefile("./inventory.tmpl",
  {
    cat = "victim1",
    ip_addrs = [aws_instance.ghh-ubuntu-ec2.public_ip]
    vars = [
      "ansible_user: ubuntu",
      "ansible_python_interpreter: /usr/bin/python3",
      "ansible_ssh_private_key_file: /home/kali/.ssh/id_rsa"
      ]
  }
  )
  filename = "../ansible/inventory/victim1.yml"
}

