#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import protocol
from guest import Guest
from code import Code
from enum import Enum

class OOBType(Enum):
    Print = 0

with Guest() as g:
    for (msg_type, body) in g.messages():
        if msg_type == protocol.MT.OOB:
            oob_type, *msg = body
            
            if oob_type == OOBType.Print.value: 
                fmt, *args = msg
                print(f'PRINT: {fmt % tuple(args)}')

        if msg_type == protocol.MT.Boot:
            print('BOOTED')
            g.execute(
                Code("""
                    OOB_PRINT "hello world!"
                    REPLY_EMPTY
                    ret""", g.symbols))

        if msg_type == protocol.MT.Reply:
            print(f'REPLY: {body}')
