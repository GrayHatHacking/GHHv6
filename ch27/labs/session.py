#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import signal
import protocol
from enum import Enum
from guest import Guest
from code import Code

class OOBType(Enum):
    Print = 0
    Assert = 1

class Session:
    debug = True
    retry_exceptions = True
    timeout = 3

    def __init__(self, guest_cls=Guest):
        self.guest_cls = guest_cls
        self.regs = (
            'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp',
            'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'
            )
        signal.signal(signal.SIGALRM, self.timeout_handler)

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

    def execute(self, code):
        self.guest.execute(self.code(code))

    def fuzz(self, reply):
        raise NotImplementedError

    def on_boot(self, body):
        self.context_area = self.guest.memory.alloc(0x1000)
        self.install_idt()

    def install_idt(self, vectors=30):
        entries = (f'{l:#x}, {h:#x}'
            for l, h in map(self.make_vector_handler, range(vectors)))
        self.execute(
            f"""lidt [idtr]
                ret
                align 16
                idtr:
                dw idt_end - idt - 1 ; IDT limit
                dq idt               ; IDT base
                align 16
                idt: dq {', '.join(entries)}
                idt_end:
            """)

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
                       xor rax, rax
                       mov dr6, rax
                       mov rax, [rsp+0x10]
                       mov [_rip], rax
                       mov rax, [rsp+0x20]
                       mov [_rflags], rax
                       mov rax, [rsp+0x28]
                       mov [_rsp], rax
                       pop rax
                       OOB_PRINT "#{vec:02}: {fmt}", UInt64, {args}
                       mov rax, cr2
                       mov rcx, [rsp]
                       OOB_PRINT "CR2 %016lx, err code %d", UInt64, rax, UInt64, rcx 
                       {code}
                       _rip:    dq 0
                       _rflags: dq 0
                       _rsp:    dq 0
                    """

        address = self.guest.op_write(self.code(err_code + code))
        return ((address & 0xffff) | 0x80000 | (
            ((address & 0xffff << 16) | 0x8f << 8) << 32), address >> 32)

    def is_oob(self, msg_type, body):
        if msg_type == protocol.MT.OOB:
            oob_type, *msg = body
            
            if oob_type == OOBType.Print.value: 
                fmt, *args = msg
                print(f'PRINT: {fmt % tuple(args)}')

            if oob_type == OOBType.Assert.value: 
                exp, _file, line = msg
                print(f'ASSERT {_file}:{line}: {exp}')

            return True
        else:
            return False

    def is_boot(self, msg_type):
        return msg_type == protocol.MT.Boot

    def next_message(self):
        msg = next(self.messages)

        while self.is_oob(*msg):
            msg = next(self.messages)

        return msg

    def run(self):
        while True:
            try:
                with self.guest_cls() as self.guest:
                    self.messages = self.guest.messages()
                    self.run_loop()

            except Exception as e:
                if self.retry_exceptions is False:
                    raise
    
                print(f'exception: {e}')

    def run_loop(self):
        while True:
            signal.alarm(0)
            signal.alarm(self.timeout)
            msg_type, body = self.next_message()

            if self.is_boot(msg_type):
                self.on_boot(body)
            else:
                self.on_reply(body)

