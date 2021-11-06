output "victim2" {
  value = try(aws_instance.ghh-ubuntu-test.public_ip,null)
}

output "victim2-instance" {
  value = try(aws_instance.ghh-ubuntu-test.id,null)
}