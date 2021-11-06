#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 and texttable to print
# userData from EC2 instances from each region

# TODO: Better API Key Support?
# API keys currently are loaded from a profile
# Better secret key handling?
# TODO: Better error handling
import boto3, os, base64, argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_ssh_public_key, load_pem_private_key, load_ssh_private_key
from texttable import Texttable

argparser = argparse.ArgumentParser(description='Attempts to decrypt the default password for a Windows host')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('region', help='The AWS region that you want to do everything in')
argparser.add_argument('keyfile', help='Path to keyfile associated with the instance')
args = argparser.parse_args()

#This function decrypts the password using the EC2 private key from the pem
def decrypt(ciphertext, keyfile=args.keyfile):
    with open(keyfile, "rb") as key_file:
        private_key = load_ssh_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
    )
    plaintext = private_key.decrypt(
         ciphertext,padding.PKCS1v15()
    )
    return plaintext

##You may need to adjust the region?
#This loads the aws profile called 'default'
session = boto3.session.Session(profile_name='default', region_name=args.region)
client = session.client('ec2', args.region)
#write the top of the csv
table = Texttable()
table.set_cols_align(["c", "c", "c", "c", "c"])
table.set_cols_valign(["m", "m", "m", "m", "m"])
table.set_cols_width([20,15,15,15, 32])
table.header(["Instance ID", "Name", "PrivateIpAddress", "PublicIpAddress", "Password"])
def get_ec2_info():
    #load all the reservations
    reservations = client.describe_instances()
    #iterate through all of the reservations and instances.
    for reservation in reservations['Reservations']:
        for instance in reservation["Instances"]:
            # Get the encrypted password and decrypt
            data = client.get_password_data(InstanceId=instance['InstanceId'])
            if client.get_password_data(InstanceId=instance['InstanceId'])['PasswordData']:
                password = decrypt(base64.b64decode(data['PasswordData'])).decode('ascii')
                #print the instance ID, private IP and password as the for loops iterate
                #TODO Not sure if this works well with multiple tags.
                if instance['Tags'][0]['Value']:
                    name = instance['Tags'][0]['Value']
                else:
                    name = ' '
                if instance['PublicIpAddress']:
                    publicip = instance['PublicIpAddress']
                else:
                    publicip = ' '
                table.add_row([instance['InstanceId'], name , instance['PrivateIpAddress'], publicip ,  password])
get_ec2_info()
print(table.draw())

