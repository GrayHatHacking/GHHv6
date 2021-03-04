#!/bin/bash
RED='\033[0;31m'
WHITE='\033[0;37m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

imagelist=(ghh-server2016 ghh-server2019 ghh-kali)

for i in ${imagelist[@]}; do
	latest=`aws ec2 describe-images --owner=self --filter "Name=name,Values=$i-*" --query "Images[*].[Name,ImageId,CreationDate ]" --output text --profile=ghh --region=us-east-1| sort -k3 -r | head -1| cut -f 2`
	all=`aws ec2 describe-images --owner=self --filter "Name=name,Values=$i-*" --query "Images[*].[ImageId]" --output text --profile=ghh --region=us-east-1`
	printf "${WHITE}[=] Searching for $i, found latest $latest{$NC}\n"
	for img in $all; do
		if [ $img == $latest ]; then
			printf "${GREEN}[*] Skipping delete of latest image $img${NC}\n"
		else
			printf "${RED}[-] Dereistering old image $img${NC}\n"
			aws ec2 deregister-image --image $img --profile=ghh --region=us-east-1
			
		fi
	done
	printf "${NC}\n"

done
