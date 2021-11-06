# Gray Hat Hacking v6 Lab 29
This directory contains the components to build the labs for Chapter 29.

## Lab Information  
The following VMs will be setup for this lab:
- Docker Host
  - IP: 10.0.0.50
  - Docker User: ubuntu
  - Docker Password: SSH key setup with the lab
- Kali Computer
  - IP: 10.0.0.40
  - Kali User: kali
  - Kali Password: SSH key setup with the lab

## Setting up the Lab    
1. Make sure you have completed all the steps at (https://github.com/GrayHatHacking/GHHv6/tree/main/CloudSetup).
2. Go into the Lab/terraform directory and modify the `terraform.tfvars`. Edit
   the file with your favorite text editor and then replace the contents of the
   key_path variable with the path to your SSH key. An example might look like:
   `key_path="/home/kali/.ssh/id_rsa`
3. Go into the Lab subdirectory and run `build.sh` to start the environment
   build. It will ask you are sure you want to create resources. If it does ask
   type `yes`
4. This will create resources that may cost you money. If you want to destroy
   the lab between uses, run `destroy.sh`. Answer `yes` when it asks if you are
   sure, and the resources will be deleted.
   
## Retrieving the IP addresses of the machines
Once the build.sh script is completed, it should print the IP addresses of the
hosts out to the screen. If you forget these IP addresses, you can go into the
terraform directory in the lab and type in "terraform show" and it will show
you the status of your lab as well as show you the IP addresses of the relevant
boxes.

## What does each machine do?

### Docker Host
This is the system that you will be attacking during the lab. The system itself
is running a Docker Instance with a Web Service on it. This system is the only
system that you will need to be attacking during the lab.

### Kali box
This is the box you will use as the attacker platform.

## Notes
By default this lab allows ANYONE who knows the credentials to connect to it.
For new users it may be confusing to figure out where they are connecting from.
If you would like to make this more secure, you can limit the lab to your IP
only by adding a line into the `terraform.tfvars` file that contains allow list
information like this:   
`ip_allowlist = ["1.2.3.4/32","4.5.6.7/24"]`

