#!/bin/bash

cd terraform 
terraform init && terraform validate && terraform apply
cd ../ansible
ansible-playbook -i inventory ch07_playbook.yml
