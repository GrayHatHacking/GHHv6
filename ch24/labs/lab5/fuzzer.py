#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import random
import signal
import protocol
from enum import Enum
from guest import Guest
from code import Code

class OOBType(Enum):
    Print = 0
    Assert = 1

class Fuzzer:
    regs = ('rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp',
            'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15')
    debug = False

    def __init__(self, seed):
        self.rand = random.Random(seed)
        signal.signal(signal.SIGALRM, Fuzzer.timeout_handler)

    @staticmethod
    def timeout_handler(signum, frame):
        raise Exception('TIMEOUT')

    def context_save(self):
        return 'pop rax\n' + '\n'.join(
            f'mov qword [{self.context_area + n*8:#x}], {reg}'
            for (n, reg) in enumerate(self.regs)) + '\n'
    
    def context_restore(self):
        return '\n'.join(
            f'mov {reg}, qword [{self.context_area + n*8:#x}]'
            for (n, reg) in enumerate(self.regs)) + '\njmp rax\n'

    def code(self, code):
        return Code(code, self.guest.symbols)

    def fuzz(self, reply):
        raise NotImplementedError

    def on_boot(self, body):
        self.fuzz([])

    def handle_message(self, msg_type, body):
        if msg_type == protocol.MT.OOB:
            oob_type, *msg = body
            
            if oob_type == OOBType.Print.value: 
                fmt, *args = msg
                print(f'PRINT: {fmt % tuple(args)}')

            if oob_type == OOBType.Assert.value: 
                exp, _file, line = msg
                print(f'ASSERT {_file}:{line}: {exp}')
        else:
            if msg_type == protocol.MT.Boot:
                self.context_area = self.guest.memory.alloc(0x1000)
                self.on_boot(body)
            else:
                self.fuzz(body)

    def run(self):
        while True:
            try:
                with Guest() as self.guest:
                    for msg in self.guest.messages():
                        signal.alarm(0)
                        signal.alarm(2)
                        self.handle_message(*msg)

            except Exception as e:
                print(f'exception: {e}')
