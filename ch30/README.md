# Gray Hat Hacking v6 Lab 30
This directory contains the components to build the labs for Chapter 30.

## Lab Information  
The following VMs will be setup for this lab:
Amazon Elastic Kubernetes Stack:
- EKS Service (Run by AWS)
- EC2 Instance for the EKS Node (t2.medium size)
Kubernetes:
- Sock Shop Microservices Demo
- Bash Container

## Setting up the Lab    
1. Make sure you have completed all the steps at (https://github.com/GrayHatHacking/GHHv6/tree/main/CloudSetup).
2. Go into the Lab directory run `build.sh` to start the environment.
3. Once the environment is built, you will have the appropriate links.
4. This will create resources that may cost you money. If you want to destroy
   the lab between uses, run `destroy.sh`. Answer `yes` when it asks if you are
   sure, and the resources will be deleted.
   
## Retrieving the URL of the individual endpoints
Once the build.sh script is completed, it should print the URL addresses of the
EKS API Server and the Sock Shop service out to the screen. If you forget these
you can run the following commands:

To get the Sock Shop URL: 
```kubectl get svc -n sock-shop | grep front | awk '{ print $4 }'```

To get the Kubernetes API Server URL:
```cat ~/.kube/config | grep server | awk '{ print $2 }'```
