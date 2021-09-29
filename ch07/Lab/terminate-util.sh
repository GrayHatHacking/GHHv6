#!/bin/bash
instance=`jq -r '.resources[] |select( .name == "ghh_util") |  .instances[0].attributes.id ' terraform/terraform.tfstate `
if [ -z "$instance" ]; then
	echo "Could not locate instance ID in terraform/terraform.tfstate"
	exit
fi
if aws ec2 describe-instances --instance-id $instance --profile=ghh --region=us-east-1  ; then
	aws ec2 terminate-instances --instance-id $instance --profile=ghh --region=us-east-1
else
	echo "Instance did not seem to exist"
fi
