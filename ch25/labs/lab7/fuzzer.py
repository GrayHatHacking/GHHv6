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
        self.install_idt()
        self.fuzz([])

    def install_idt(self, vectors=30):
        entries = (f'{l:#x}, {h:#x}'
            for l, h in map(self.make_vector_handler, range(vectors)))
        self.guest.op_exec(
            self.guest.op_write(
               self.code(f"""lidt [idtr]
                             ret
                             align 16
                             idtr:
                             dw idt_end - idt - 1 ; IDT limit
                             dq idt               ; IDT base
                             align 16
                             idt: dq {', '.join(entries)}
                             idt_end:
                             """)))

    def make_vector_handler(self, vec):
        err_code = ''
        code = 'REPLY_EMPTY\n' + self.context_restore()

        if vec not in {8, 10, 11, 12, 13, 14, 17, 30}:
            err_code = 'push 0\n'
                        
        if self.debug:
            regs = ('rip', 'rflags') + self.regs
            fmt = ' '.join(f'{r.upper()}=%016lx' for r in regs)
            args = ', UInt64, '.join(f'qword [_{r}]'
                if r in {'rip', 'rsp', 'rflags'} else r for r in regs)
            code = f"""push rax
                       mov rax, [rsp+0x10]
                       mov [_rip], rax
                       mov rax, [rsp+0x20]
                       mov [_rflags], rax
                       mov rax, [rsp+0x28]
                       mov [_rsp], rax
                       pop rax
                       OOB_PRINT "#{vec:02}: {fmt}", UInt64, {args}
                       {code}
                       _rip:    dq 0
                       _rflags: dq 0
                       _rsp:    dq 0
                    """

        address = self.guest.op_write(self.code(err_code + code))
        return ((address & 0xffff) | 0x80000 | (
            ((address & 0xffff << 16) | 0x8f << 8) << 32), address >> 32)

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
