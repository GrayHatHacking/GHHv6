#!/bin/bash
terraform state rm aws_vpc.this
terraform state rm aws_subnet.this 
terraform state rm aws_security_group.ghh-ec2-security-group
terraform destroy -auto-approve
