#!/bin/bash
if [[ ! -f /usr/local/bin/kubectl ]]
then
  curl -LO https://dl.k8s.io/release/v1.21.0/bin/linux/amd64/kubectl 
  chmod a+x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
fi

cd terraform
terraform init
terraform apply -auto-approve

export KOPS_STATE_STORE=s3://$(terraform output -json aws_s3 | jq -r)
kops create cluster --vpc=$(terraform output -json vpc_id | jq -r) --master-zones=$(terraform output -json networks | jq -r '.[].availability_zone' | paste -sd, -) --zones=$(terraform output -json networks | jq -r '.[].availability_zone' | paste -sd, -) --subnets=$(terraform output -json subnet_ids | jq -r 'join(",")') --networking=calico --node-count=3 --master-size=t2.medium --node-size=t2.medium --dns=private --name=kops.ghh.hack --yes
