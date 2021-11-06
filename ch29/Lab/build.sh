#!/bin/bash

echo "[+] Building out the targets with Terraform"
cd terraform
terraform init
terraform apply -auto-approve
cd ..

echo "[+] Using ansible to lay down the vulns"
cd ansible
ansible-playbook -i inventory ch29_playbook.yml
cd ..

echo "[+]You can now login to kali, here is the inventory files with IP addresses"
cat ansible/inventory/*
