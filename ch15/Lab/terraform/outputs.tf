output "target_password" {     value = rsadecrypt(aws_instance.ghh_target.password_data, file(var.key_path)) }

output "target_ip" { value =  try(aws_instance.ghh_target.public_ip,null) }
output "kali_ip" { value =  try(aws_instance.kali.public_ip,null) }




resource "local_file" "target_inv" {
 content = templatefile("./inventory.tmpl",
 {
  cat = "target",
  ip_addrs = [aws_instance.ghh_target.public_ip]
  vars = ["ansible_connection: winrm",
	"ansible_user: Administrator",
	"ansible_winrm_scheme: http",
        "ansible_winrm_transport: basic",
        "ansible_winrm_server_cert_validation: ignore",
        "ansible_winrm_port: 5985",
        "ansible_password: ${var.dc_password}"
        ]
 }
 )
 filename = "../ansible/inventory/target.yml"
}
resource "local_file" "kali_inv" {
 content = templatefile("./inventory.tmpl",
 {
  cat = "kali",
  ip_addrs = [aws_instance.kali.public_ip]
  vars = [
	"ansible_user: kali",
        "ansible_python_interpreter: /usr/bin/python3"
        ]
 }
 )
 filename = "../ansible/inventory/kali.yml"
}
