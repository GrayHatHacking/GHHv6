output "kali_ip" { value =  try(aws_instance.kali.public_ip,null) }

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

output "vpc_id" {
  value = aws_vpc.this.id
}

data "aws_subnet_ids" "subnet_ids" {
  depends_on = [
    aws_subnet.subnets
  ]
  vpc_id = aws_vpc.this.id
}

output "subnet_ids" {
  value = data.aws_subnet_ids.subnet_ids.ids.*
}

output "networks" {
  value = var.networks
}
