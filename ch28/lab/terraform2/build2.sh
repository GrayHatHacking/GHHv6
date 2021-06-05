#!/bin/bash
terraform init
VPCID=$(cd ../terraform; terraform output | grep vpc | awk -F\" '{ print $2}')
SUBNET=$(cd ../terraform; terraform output | grep subnet | awk -F\" '{ print $2}')
terraform import aws_vpc.this $VPCID
terraform import aws_subnet.this $SUBNET
terraform apply
