#!/bin/bash
TARGET_IP=`jq -r '.resources[] | select(.name == "ghh_target")| .instances[0].attributes.public_ip' terraform/terraform.tfstate`
KALI_IP=`jq -r '.resources[] | select(.name == "kali")| .instances[0].attributes.public_ip' terraform/terraform.tfstate`
if [ -z "$TARGET_IP" ]; then
	echo "Could not locate instance ID in terraform/terraform.tfstate"
	exit
fi
echo -e "Kali IP: $KALI_IP\nTarget IP: $TARGET_IP\n"
