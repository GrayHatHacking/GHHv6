#!/bin/bash

AWS=`which aws`
JQ=`which jq`

if ! test -f "$AWS"; then
	echo "AWS cli is required for execution, please install and try again"
	exit
fi
if ! test -f "$JQ"; then
	echo "JQ is required for execution, please install and try again"
	exit
fi
if ! test -f "key-out.json"; then 
	echo "Cannot deproision without the key-out.json file"
	exit
fi

aws iam remove-user-from-group --user-name ghh --group-name ghh-group
aws iam detach-group-policy --group-name ghh-group --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam detach-group-policy --group-name ghh-group --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-group-policy --group-name ghh-group --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
aws iam detach-group-policy --group-name ghh-group --policy-arn arn:aws:iam::aws:policy/AmazonSSMFullAccess
aws iam detach-group-policy --group-name ghh-group --policy-arn arn:aws:iam::aws:policy/AmazonRoute53FullAccess
aws iam delete-group --group-name ghh-group
aws iam delete-access-key --user-name ghh  --access-key-id `jq .AccessKey.AccessKeyId  key-out.json | cut -f 2 -d '"'`
aws iam delete-user --user-name ghh 
