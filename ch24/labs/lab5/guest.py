#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import protocol
from enum import Enum
from subprocess import Popen, PIPE
from remotemem import RemoteMemory

class OpType(Enum):
    Write = 0
    Exec = 1

class Guest:
    def __init__(self):
        self.proc = None
        self.memory = None
        self.symbols = None
        self._request = []

    def __enter__(self):
        self.proc = Popen(
            'exec qemu-system-x86_64 -display none -boot d -cdrom kernel_bios.iso -m 300M -serial stdio -enable-kvm',
             stdout=PIPE, stdin=PIPE, shell=True
        )
        return self

    def __exit__(self, type, value, traceback):
        self.proc.kill()

    def _init_boot_info(self, symbols, mmap):
        self.symbols = dict(symbols)
        self.memory = RemoteMemory()

        for entry in map(dict, mmap):
            if entry['type'] == 1:  # MULTIBOOT_MEMORY_AVAILABLE
                self.memory.add_region(entry['address'], entry['length'])

        kernel_end = (self.symbols['_end'] + 0x1000) & ~0xfff 
        self.memory.del_region(0, kernel_end)

    def messages(self):
        while self.proc.returncode is None:
            msg = protocol.recv(self.proc.stdout)
            msg_type, body = msg

            if msg_type == protocol.MT.Boot:
                self._init_boot_info(**dict(body))

            yield msg

    def op_write(self, code, address=None):
        if address is None:
            address = self.memory.alloc(len(code.build(0)))
        
        self._request += [
            protocol.f.UInt32(OpType.Write.value),
            protocol.f.UInt64(address),
            tuple(protocol.f.UInt8(x) for x in code.build(address))
        ]
        return address

    def op_exec(self, address):
        self._request += [
            protocol.f.UInt32(OpType.Exec.value),
            protocol.f.UInt64(address)
        ]

    def op_commit(self):
        protocol.send(self.proc.stdin, self._request)
        self._request.clear()

    def execute(self, code):
        address = self.op_write(code)
        self.op_exec(address)
        self.op_commit()
        self.memory.free(address)
