data "amazon-ami" "ghh_kali" {
  filters = {
    name                = "debian-10-amd64*"
    root-device-type    = "ebs"
    virtualization-type = "hvm"
  }
  most_recent = true
  owners      = ["136693071363"]
  profile     = "ghh"
  region      = "us-east-1"
}

# "timestamp" template function replacement
locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

source "amazon-ebs" "ghh_kali" {
  ami_name      = "ghh-kali-${local.timestamp}"
  instance_type = "m3.large"
  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/xvda"
    volume_size           = 40
    volume_type           = "standard"
  }
  profile      = "ghh"
  region       = "us-east-1"
  source_ami   = "${data.amazon-ami.ghh_kali.id}"
  ssh_username = "admin"
}

build {
  sources = ["source.amazon-ebs.ghh_kali"]
  # This block can be enabled if you want to keep a SSH key for troubleshooting
  #provisioner "shell-local" {
      #inline = ["echo '${build.SSHPrivateKey}' > /tmp/'${build.Host}'-session.pem"]
  #}

  provisioner "file" {
    destination = "/tmp/config.sh"
    source      = "config.sh"
  }

  provisioner "shell" {
    expect_disconnect = "true"
    inline            = ["chmod 755 /tmp/config.sh", "sudo /tmp/config.sh"]
    skip_clean = "true"
    
  }
# This block can be enabled if you need to troubleshoot and pause builds to SSH and see what is happening
#  provisioner "breakpoint" {
#    disable = false
#    note    = "this is a breakpoint"
#  }

}
