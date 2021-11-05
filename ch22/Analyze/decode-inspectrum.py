#!/usr/bin/env python

import bitstring
from bitstring import BitArray, BitStream

def decode(pfx,thresh,symbols):
    symbolString=''

    for i in symbols:
        if i>thresh:
            symbolString+='1'
        else:
            symbolString+='0'

    hexSymbols =BitArray('0b'+symbolString)
    convertedSymbols = hexSymbols.hex.replace('e','1').replace('8','0')
    print("{0:<12s} {1}".format(pfx,hexSymbols))
    print("{0:<12s} {1}".format(pfx,BitArray('0b'+convertedSymbols[:-1])))
    print(symbolString)
    
