The following instructions are for all AWS labs in this book.  There are separate instructions for Azure, inside Chapter 8, of the book.

###### Cloud Setup Instructions
1. Signup for an AWS account   
Go to https://aws.amazon.com and signup for a new account

2. These have been designed to run under a *nix installation. This can be done with a downloaded Kali (https://www.kali.org/downloads/)
installation, your favorite *nix implementation of choice, or Windows Subsystem for Linux 
   (https://docs.microsoft.com/en-us/windows/wsl/install-win10). 
   Alternatively, if you want to do this all in the cloud, once you've signed into your account go to Amazon CloudShell. If you do this, make sure it has its own tab, you will need to copy/paste information from other pages in the Amazon AWS console.

3. Install the following items:    
AWS Cli (https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)     
   Packer (https://learn.hashicorp.com/tutorials/packer/getting-started-install)     
   Terraform (https://learn.hashicorp.com/tutorials/terraform/install-cli     
   Ansible (https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)     
   jq (apt-get install jq or https://stedolan.github.io/jq/)

   If you are using Amazon CloudShell, run these commands
```
git clone https://github.com/GrayHatHacking/GHHv6.git    
cd GHHv6/CloudSetup
bash install-cloud-tools.sh    
. ~/.bash_profile     
```
   If you are using Kali Linux, run these commands
```
git clone https://github.com/GrayHatHacking/GHHv6.git      
sudo apt-get update   
sudo apt-get install awscli packer software-properties-common ansible jq   
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -   
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com buster main"   
sudo apt-get update && sudo apt-get install terraform   
```
 
4. In the AWS console, go to "My Security Credentials"<BR>
![My Security Credential Image](https://github.com/GrayHatHacking/GHHv6/blob/main/CloudSetup/images/aws-signup-1.png) <BR>
   Go to access keys and Click "New Access Key"<BR>
![New Access Keys image](https://github.com/GrayHatHacking/GHHv6/blob/main/CloudSetup/images/aws-signup-2.png) <BR>
   Download the key file <BR>
![Download Key file](https://github.com/GrayHatHacking/GHHv6/blob/main/CloudSetup/images/aws-signup-3.png) <BR>
   
5. Open the file in an editor, then open a console window and type in:
   `aws configure` <BR>
![AWS configure Image](https://github.com/GrayHatHacking/GHHv6/blob/main/CloudSetup/images/aws-signup-4.png) <BR>
   Add the access key and the secret key from the file to the configuration and choose `us-east-1` for the region.<BR>
   this region has all the AWS features we will need, so it is a safe default. For default output format, choose `json`.
   
6. If you have not already done so, execute a git clone of this repository:    
   `git clone https://github.com/GrayHatHacking/GHHv6.git`   
    Change directory into the CloudSetup directory and then run the `provision.sh` file. This will create all of the necessary roles and permissions that will be needed for the
exercises in the book. It will create a new user called `ghh` and a new profile called `ghh` so that all of the examples
   will work without modification.
   
7. SSH keys will be needed for these exercises. If you have not created one then run `ssh-keygen` to 
generate a new key pair. The result should be a file in `~/.ssh/` called `id_rsa` and one called `id_rsa.pub`. 
   These files will be used to generate a key for use in AWS to SSH from and will make the rest of the examples easier.
   
8. Create the keypair in AWS:<BR>
`aws ec2 import-key-pair --key-name ghh --public-key-material fileb://~/.ssh/id_rsa.pub --profile=ghh --region=us-east-1`
   
9. Run `build-images.sh` to build the base images for the rest of the exercises. This will take a few minutes to an hour.  


   

