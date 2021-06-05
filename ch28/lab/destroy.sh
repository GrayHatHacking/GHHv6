#!/bin/bash
cd terraform2
./destroy2.sh
cd ..
cd terraform
aws cloudformation delete-stack --stack-name UserDataSwap
terraform destroy -auto-approve
