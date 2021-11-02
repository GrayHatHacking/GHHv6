#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import time
import pci
import construct as c
from remotemem import PageAlloc, IOVector

USB_DIR_OUT = 0
USB_DIR_IN = 0x80
USB_REQ_GET_DESCRIPTOR = 0x06
USB_DT_STRING = 0x03

class Session(pci.Session):
    dump_only = False

    @staticmethod
    def qtd_token(transfer_bytes, pid):
        CERR = (1 << 10)
        Status = 1 << 7 # Active
        return (transfer_bytes << 16) | CERR | (pid << 8) | Status

    @staticmethod
    def qtd_single(token, data=None):
        if data is not None:
            buffer_list = data.page_list()
        else:
            buffer_list = []

        if len(buffer_list) > 5:
            print('Error: buffers too big')
            exit(1)

        buffer_list += [0] * (5 - len(buffer_list))
        return c.Struct(
            'next_qtd'     / c.Int32ul,
            'alt_next_qtd' / c.Int32ul,
            'token'        / c.Int32ul,
            'buffer_list'  / c.Array(5, c.Int32ul)
        ).build({
            'next_qtd':     1, # terminate
            'alt_next_qtd': 1, # terminate
            'token':        token,
            'buffer_list':  buffer_list
        })
    
    @staticmethod
    def qh_single(qh, qtd):
        return c.Struct(
            'next_qh'        / c.Int32ul,
            'endpoint_chars' / c.Int32ul,
            'endpoint_caps'  / c.Int32ul,
            'current_qtd'    / c.Int32ul,
        ).build({
            'next_qh':        qh | (0b01 << 1), # QH Typ
            'endpoint_chars': 1 << 15,          # H flag
            'endpoint_caps':  0,
            'current_qtd':    qtd,
        })

    def port_reset(self):
        self.execute(
            f"""{self.context_save()}
                mov rax, {self.PORTSC0:#x}
                mov dword [rax], 1 << 8   ; Port Reset
                mov dword [rax], 1 << 2   ; Port Enabled
                {self.context_restore()}
            """)
                
    def async_sched_stop(self):
        self.execute(
            f"""{self.context_save()}
                mov rbx, {self.USBCMD:#x}
                mov dword [rbx], 1        ; Async Schedule disable
                mov rdx, {self.USBSTS:#x}
                poll:                     ; Wait for disable
                mov eax, dword [rdx]
                test eax, 1 << 15         ; Async schedule status
                jnz poll
                {self.context_restore()}
            """)

    def async_sched_run(self, qh):
        self.execute(
            f"""{self.context_save()}
                mov rbx, {self.USBCMD:#x}
                mov rax, {self.ASYNCLISTADDR:#x}
                mov rdx, {self.USBSTS:#x}
                mov dword [rax], {qh:#x}
                mov dword [rbx], (1 << 5) | 1 ; Async Schedule enable
                poll:                         ; Wait for enable
                mov eax, dword [rdx]
                test eax, 1 << 15             ; Async schedule status
                jz poll
                {self.context_restore()}
            """)

    def run_single(self, token, qtd_data):
        pages = PageAlloc(self.guest.memory, 0x2000)
        qh_addr = pages.start()
        qtd_addr = qh_addr + 0x100
        self.async_sched_stop()
        qh = self.qh_single(qh_addr, qtd_addr)
        qtd = self.qtd_single(token, qtd_data)
        overlay_addr = qh_addr + len(qh)
        self.guest.op_write_data(qh, qh_addr)
        self.guest.op_write_data(qtd, overlay_addr)
        self.guest.op_write_data(qtd, qtd_addr)
        self.async_sched_run(qh_addr)
        pages.free()

    @staticmethod
    def request(req_type, request, value, index, length):
        return c.Struct(
            'bmRequestType' / c.Int8ul,
            'bRequest'      / c.Int8ul,
            'wValue'        / c.Int16ul,
            'wIndex'        / c.Int16ul,
            'wLength'       / c.Int16ul
        ).build({
            'bmRequestType': req_type,
            'bRequest':      request,
            'wValue':        value,
            'wIndex':        index,
            'wLength':       length
        })

    def setup(self, request):
        SETUP_TOKEN = 0b10
        data = PageAlloc(self.guest.memory, 0x1000)
        self.guest.op_write_data(request, data.start())
        self.run_single(self.qtd_token(8, SETUP_TOKEN), data)
        data.free()

    def usb_in(self, data_len):
        IN_TOKEN = 0b01
        pages = PageAlloc(self.guest.memory, data_len)
        self.run_single(self.qtd_token(data_len, IN_TOKEN), pages)
        self.execute(
            f"""{self.context_save()}
                PUT_VA Array, array_h, {pages.start():#x}
                REPLY
                {self.context_restore()}
                array_h: dd {data_len:#x}, UInt8
            """)
        _, data = self.next_message()
        pages.free()
        return bytes(data[0])

    def usb_out(self, data: IOVector):
        OUT_TOKEN = 0b00
        data_len = data.size()
        pages = PageAlloc(self.guest.memory, data_len)

        for chunk in data.iter():
            self.guest.op_write_data(chunk.data, pages.start() + chunk.offset)

        self.run_single(self.qtd_token(data_len, OUT_TOKEN), pages)
        pages.free()

    def desc_string(self, index):
        value = (USB_DT_STRING << 8) | index
        req = USB_REQ_GET_DESCRIPTOR
        self.setup(self.request(USB_DIR_IN, req, value, 0, 255))
        data = c.Struct(
            'bLength' / c.Int8ul,
            'type'    / c.Int8ul,
            'str'     / c.Bytes(lambda this: this.bLength - 2)
        ).parse(self.usb_in(255))

        if self.debug:
            print(data)

        if len(data.str) == 0:
            return b'\0'

        return data.str[::2]

    def ehci_regs_base(self):
        for bus in self.pci:
            for slot in self.pci[bus]:
                for func in self.pci[bus][slot]:
                    dev = self.pci[bus][slot][func]

                    if dev.class_code == 0x0c and \
                        dev.subclass == 0x03 and \
                        dev.prog_if == 0x20:
                        return dev.bars[0].bar
        return None

    def on_boot(self, body):
        super().on_boot(body)
        regs_base = self.ehci_regs_base()

        if regs_base is None:
            print('ERROR: EHCI not found')
            exit(0)

        self.execute(f"""
            {self.context_save()}
            mov rax, {regs_base:#x}
            mov al, byte [rax]
            PUT_VA UInt8, rax
            REPLY
            {self.context_restore()}
            """)
        CAPLENGTH = self.next_message()[1][0]
        self.USBCMD = regs_base + CAPLENGTH + 0x00
        self.USBSTS = regs_base + CAPLENGTH + 0x04
        self.ASYNCLISTADDR = regs_base + CAPLENGTH + 0x18
        self.PORTSC0 = regs_base + CAPLENGTH + 0x44


