#!/bin/bash
pip3 install --user ansible pywinrm
wget https://releases.hashicorp.com/terraform/0.14.5/terraform_0.14.5_linux_amd64.zip
wget https://releases.hashicorp.com/packer/1.6.6/packer_1.6.6_linux_amd64.zip
unzip terraform*.zip -d ~/.local/bin/
unzip packer*.zip -d ~/.local/bin/
rm terraform*.zip
rm packer*.zip
echo -e "PATH=\$HOME/.local/bin:\$PATH\nexport PATH\n" >> .bash_profile

echo -e  "Cloud tools installed.. to add them to your path type in:\n  . .bash_profile\n"
