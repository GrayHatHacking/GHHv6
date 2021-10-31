#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import session
import hyperv_guest
import construct as c
from code import Code
from remotemem import PageAlloc
from capstone import *

HV_MESSAGE_PAYLOAD_BYTE_COUNT = 240

HvMessageHeader = c.Struct(
    'MessageType'  / c.Int32ul,
    'PayloadSize'  / c.Int8ul,
    'MessageFlags' / c.Int8ul,
    'Reserved'     / c.Int16ul,
    'Sender'       / c.Int64ul
)

HvMessage = c.Struct(
    'Header'  / HvMessageHeader,
    'Payload' / c.Bytes(HV_MESSAGE_PAYLOAD_BYTE_COUNT)
)

HvCallPostMessageInput = c.Struct(
    'ConnectionId' / c.Int32ul,
    'RsvdZ'        / c.Const(0, c.Int32ul),
    'MessageType'  / c.Int32ul,
    'PayloadSize'  / c.Int32ul,
    'Message'      / c.Bytes(HV_MESSAGE_PAYLOAD_BYTE_COUNT)
)

HvCallSignalEventInput = c.Struct(
    'ConnectionId' / c.Int32ul,
    'FlagNumber'   / c.Int16ul,
    'RsvdZ'        / c.Const(0, c.Int16ul),
)

class Session(session.Session):
    dump_contents = False
    retry_exceptions = False
    timeout = 0

    def __init__(self):
        super().__init__(hyperv_guest.GuestGen2)

    def HvCallPostMessage(self, ConnectionId, MessageType, payload):
        input = HvCallPostMessageInput.build({
            'ConnectionId': ConnectionId,
            'MessageType': MessageType,
            'PayloadSize': len(payload),
            'Message': payload.ljust(HV_MESSAGE_PAYLOAD_BYTE_COUNT, b'\0')
        })
        self.guest.op_write_data(input, self.hv_postmsg_input)
        code = self.code(
            f"""
            {self.context_save()}
            mov rcx, 0x005C
            mov rdx, {self.hv_postmsg_input:#x}
            call {self.hc_page:#x}
            PUT_VA UInt64, rax
            REPLY
            {self.context_restore()}
            """)
        self.guest.execute(code)
        _, result = self.next_message()
        return result[0]

    def HvCallSignalEvent(self, ConnectionId, FlagNumber):
        input = HvCallSignalEventInput.build({
            'ConnectionId': ConnectionId,
            'FlagNumber': FlagNumber
        })
        input = int.from_bytes(input, 'little')
        code = self.code(
            f"""
            {self.context_save()}
            mov rcx, 0x005D | (1 << 16) ; use fast hypercall
            mov rdx, {input:#x}
            call {self.hc_page:#x}
            PUT_VA UInt64, rax
            REPLY
            {self.context_restore()}
            """)
        self.guest.execute(code)
        _, result = self.next_message()
        return result[0]


    def dump_hc_page(self):
        code = self.code(
            f"""
            {self.context_save()}
            ; send contents of hypercall page to client (first 70 bytes)
            PUT_VA Array, array_h, {self.hc_page:#x}
            REPLY
            {self.context_restore()}
            array_h: dd 70, UInt8
            """
        )
        self.guest.execute(code)
        _, data = self.next_message()
        md = Cs(CS_ARCH_X86, CS_MODE_64)
        print('Hypercall page contents:')

        for i in md.disasm(bytes(data[0]), self.hc_page):
            print(f'{i.address:#x}: {i.mnemonic}\t{i.op_str}')

        exit(0)

    def on_boot(self, body):
        super().on_boot(body)
        pages = PageAlloc(self.guest.memory, 0x2000).page_list()
        (
            self.hv_postmsg_input,
            self.hc_page
        ) = pages
        guest_id = 1 << 48   # Vendor: ID Microsoft
        guest_id |= 4 << 40  # OS: Windows NT
        guest_id |= 10 << 32 # Major version: 10
        guest_id |= 18362    # Build Number:  18362    
        code = self.code(
            f"""
            {self.context_save()}
            mov rcx, 0x40000000 ; HV_X64_MSR_GUEST_OS_ID
            xor rdx, rdx
            mov rax, {guest_id:#x}
            wrmsr
            mov rcx, 0x40000001; HV_X64_MSR_HYPERCALL
            xor rdx, rdx
            ; set hypercall page GPA & enable bit
            mov rax, {self.hc_page | 1:#x}
            wrmsr
            {self.context_restore()}
            """)
        self.guest.execute(code)

        if self.dump_contents:
            self.dump_hc_page()        

if __name__ == "__main__":
    Session.dump_contents = True
    Session().run()
