#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import sys
import fuzzer
from code import Code

class Fuzzer(fuzzer.Fuzzer):
    def __init__(self, seed):
        super().__init__(seed)
        self.discovered_ports = []
        self.blacklisted_ports = list(range(0x3f8, 0x3f8 + 5))

    def fuzz(self, reply):
        if reply:
            port, value = reply

            if value != (1 << value.width) - 1 \
                and port not in self.discovered_ports: 
                print(f'New port: {port:04x} -> {value:08x}')
                self.discovered_ports.append(port)

        size = self.rand.choice((8, 16, 32))
        reg = {8: 'al', 16: 'ax', 32: 'eax'}[size]
        port = self.blacklisted_ports[0]

        while port in self.blacklisted_ports:
            if not self.discovered_ports or self.rand.choice((True, False)):
                port = self.rand.randint(0, 0xffff)
            else:        
                port = self.rand.choice(self.discovered_ports)

        op = self.rand.choice((
            f"""mov dx, {port:#x}
                in {reg}, dx
                PUT_VA UInt16, rdx, UInt{size}, rax
                REPLY
            """,
            f"""mov dx, {port:#x}
                mov {reg}, {self.rand.randint(0, (1 << size) - 1):#x}
                out dx, {reg}
                REPLY_EMPTY
            """))
        code = self.code(self.context_save() + op + self.context_restore())
        self.guest.execute(code)

if __name__ == "__main__":
    Fuzzer(int(sys.argv[1])).run()
