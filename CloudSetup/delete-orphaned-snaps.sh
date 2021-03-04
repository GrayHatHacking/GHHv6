#!/bin/bash
RED='\033[0;31m'
WHITE='\033[0;37m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

printf "${WHITE}[*] Retrieving image list${NC}\n"
snaplist=`aws ec2 describe-images --owner self --query "Images[*].[BlockDeviceMappings[0].Ebs.SnapshotId]" --output text --region=us-east-1 --profile=ghh`
printf "${WHITE}[*] Retrieving snapshot list${NC}\n"
allsnaps=`aws ec2 describe-snapshots  --owner self --profile=ghh --region=us-east-1 --query "Snapshots[*].SnapshotId" --output text`
for snap in $allsnaps; do 
	found=0
	for l in $snaplist; do
		if [ "$snap" == "$l" ]; then
			found=1
		fi
	done
	if [ $found -eq 1 ] ; then 
		printf "${GREEN}[+] Snap $snap is active${NC}\n"
	else
		printf "${RED}[-] Snap $snap is not active..Deleting${NC}\n"
		aws ec2 delete-snapshot  --snapshot-id $snap --profile=ghh --region=us-east-1
	fi

done;

