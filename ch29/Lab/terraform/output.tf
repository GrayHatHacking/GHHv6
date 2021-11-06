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

output "image_id" {
    value = data.aws_ami.ubuntu.id
}


output "docker" { value =  try(aws_instance.docker.public_ip,null) }

resource "local_file" "docker" {
  content = templatefile("./inventory.tmpl",
  {
    cat = "docker",
    ip_addrs = [aws_instance.docker.public_ip]
    vars = [
      "ansible_user: ubuntu",
      "ansible_python_interpreter: /usr/bin/python3",
      "ansible_ssh_private_key_file: /home/kali/.ssh/id_rsa"
      ]
  }
  )
  filename = "../ansible/inventory/docker.yml"
}