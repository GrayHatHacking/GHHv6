#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import session
from code import Code

devices = {
    0x00: { 0x01: 'VGA-Compatible Device' },
    0x01: {
        0x00: { 0x00: 'SCSI controller',
                0x11: 'SCSI storage device (SOP)',
                0x12: 'SCSI controller (SOP)',
                0x13: 'SCSI storage device and SCSI controller (SOP)',
                0x21: 'SCSI storage device (SOP, NVM)' },
        0x01: 'IDE controller',
        0x02: { 0x00: 'Floppy disk controller' },
        0x03: { 0x00: 'IPI bus controller' },
        0x04: { 0x00: 'RAID controller' },
        0x05: { 0x20: 'ATA controller (ADMA, single stepping)',
                0x30: 'ATA controller (ADMA, continuous)', },
        0x06: { 0x00: 'Serial ATA controller',
                0x01: 'Serial ATA controller (AHCI)',
                0x02: 'Serial Storage Bus Interface' },
        0x07: { 0x00: 'Serial Attached SCSI (SAS) controller',
                0x01: 'Obsolete' },
        0x08: { 0x00: 'NVM subsystem',
                0x01: 'NVM subsystem (NVMHCI)',
                0x02: 'NVM Express (NVMe) I/O controller',
                0x03: 'NVM Express (NVMe) administrative controller' },
        0x09: { 0x00: 'Universal Flash Storage (UFS) controller',
                0x01: 'Universal Flash Storage Host Controller Interface (UFSHCI)' },
        0x80: { 0x00: 'Other mass storage controller'},
    },
    0x02: {
        0x00: { 0x00: 'Ethernet controller' },
        0x01: { 0x00: 'Token Ring controller' },
        0x02: { 0x00: 'FDDI controller' },
        0x03: { 0x00: 'ATM controller' },
        0x04: { 0x00: 'ISDN controller' },
        0x05: { 0x00: 'WorldFip controller' },
        0x06: 'PICMG 2.14 Multi Computing',
        0x07: { 0x00: 'InfiniBand* Controller' },
        0x08: { 0x00: 'Host fabric controller' },
        0x80: { 0x00: 'Other network controller' }
    },
    0x03: {
        0x00: { 0x00: 'VGA-compatible controller',
                0x01: '8514-compatible controller' },
        0x01: { 0x00: 'XGA controller' },
        0x02: { 0x00: '3D controller' },
        0x80: { 0x00: 'Other display controller' }
    },
    0x04: {
        0x00: { 0x00: 'Video device' },
        0x01: { 0x00: 'Audio device' },
        0x02: { 0x00: 'Computer telephony device' },
        0x03: { 0x00: 'High Definition Audio (HD-A) 1.0 compatible',
                0x80: 'High Definition Audio (HD-A) 1.0 compatible' },
        0x80: { 0x00: 'Other multimedia device' },
    },
    0x05: {
        0x00: { 0x00: 'RAM' },
        0x01: { 0x00: 'Flash' },
        0x80: { 0x00: 'Other memory controller' }
    },
    0x06: {
        0x00: { 0x00: 'Host bridge' },
        0x01: { 0x00: 'ISA bridge' },
        0x02: { 0x00: 'EISA bridge' },
        0x03: { 0x00: 'MCA bridge' },
        0x04: { 0x00: 'PCI-to-PCI bridge',
                0x01: 'Subtractive Decode PCI-to-PCI bridge' },
        0x05: { 0x00: 'PCMCIA bridge' },
        0x06: { 0x00: 'NuBus bridge' },
        0x07: { 0x00: 'CardBus bridge' },
        0x08: 'RACEway bridge',
        0x09: { 0x40: 'Semi-transparent PCI-to-PCI bridge (primary)',
                0x80: 'Semi-transparent PCI-to-PCI bridge (secondary)' },
        0x0A: { 0x00: 'InfiniBand-to-PCI host bridge' },
        0x0B: { 0x00: 'Advanced Switching to PCI host bridge',
                0x01: 'Advanced Switching to PCI host bridge (ASI-SIG)' },
        0x80: { 0x00: 'Other bridge device' }
    },
    0x07: {
        0x00: { 0x00: 'Generic XT-compatible serial controller',
                0x01: '16450-compatible serial controller',
                0x02: '16550-compatible serial controller',
                0x03: '16650-compatible serial controller',
                0x04: '16750-compatible serial controller',
                0x05: '16850-compatible serial controller',
                0x06: '16950-compatible serial controller' },
        0x01: { 0x00: 'Parallel port',
                0x01: 'Bi-directional parallel port',
                0x02: 'ECP 1.X compliant parallel port',
                0x03: 'IEEE1284 controller' },
        0x02: { 0x00: 'Multiport serial controller' },
        0x03: { 0x00: 'Generic modem',
                0x01: 'Hayes compatible modem, 16450-compatible',
                0x02: 'Hayes compatible modem, 16550-compatible',
                0x03: 'Hayes compatible modem, 16650-compatible',
                0x04: 'Hayes compatible modem, 16750-compatible' },
        0x04: { 0x00: 'GPIB (IEEE 488.1/2) controller' },
        0x05: { 0x00: 'Smart Card' },
        0x80: { 0x00: 'Other communications device' }
    },
    0x08: {
        0x00: { 0x00: 'Generic 8259 PIC',
                0x01: 'ISA PIC',
                0x02: 'EISA PIC',
                0x10: 'I/O APIC interrupt controller (see Note 1 below)',
                0x20: 'I/O(x) APIC interrupt controller' },
        0x01: { 0x00: 'Generic 8237 DMA controller',
                0x01: 'ISA DMA controller',
                0x02: 'EISA DMA controller' },
        0x02: { 0x00: 'Generic 8254 system timer',
                0x01: 'ISA system timer',
                0x02: 'EISA system timers (two timers)',
                0x03: 'High Performance Event Timer' },
        0x03: { 0x00: 'Generic RTC controller',
                0x01: 'ISA RTC controller' },
        0x04: { 0x00: 'Generic PCI Hot-Plug controller' },
        0x05: { 0x00: 'SD Host controller' },
        0x06: { 0x00: 'IOMMU' },
        0x07: { 0x00: 'Root Complex Event Collector' },
        0x80: { 0x00: 'Other system peripheral' }
    },
    0x09: {
        0x00: { 0x00: 'Keyboard controller' },
        0x01: { 0x00: 'Digitizer (pen)' },
        0x02: { 0x00: 'Mouse controller' },
        0x03: { 0x00: 'Scanner controller' },
        0x04: { 0x00: 'Gameport controller (generic)',
                0x10: 'Gameport controller' },
        0x80: { 0x00: 'Other input controller' }
    },
    0x0a: {
        0x00: { 0x00: 'Generic docking station' },
        0x80: { 0x00: 'Other type of docking station' }
    },
    0x0b: {
        0x00: { 0x00: '386' },
        0x01: { 0x00: '486' },
        0x02: { 0x00: 'Pentium' },
        0x10: { 0x00: 'Alpha' },
        0x20: { 0x00: 'PowerPC' },
        0x30: { 0x00: 'MIPS' },
        0x40: { 0x00: 'Co-processor' },
        0x80: { 0x00: 'Other processors' } 
    },
    0x0c: {
        0x00: { 0x00: 'IEEE 1394 (FireWire)',
                0x10: 'IEEE 1394 following the 1394 OpenHCI specification' },
        0x01: { 0x00: 'ACCESS.bus' },
        0x02: { 0x00: 'SSA' },
        0x03: { 0x00: 'USB (UHC)',
                0x10: 'USB (OHC)',
                0x20: 'USB (EHCI)',
                0x30: 'USB (xHCI)',
                0x80: 'USB (no specific Programming Interface)',
                0xFE: 'USB device (not host controller)' },
        0x04: { 0x00: 'Fibre Channel' },
        0x05: { 0x00: 'SMBus' },
        0x06: { 0x00: 'InfiniBand (deprecated)' },
        0x07: { 0x00: 'IPMI SMIC Interface',
                0x01: 'IPMI Keyboard Controller Style Interface',
                0x02: 'IPMI Block Transfer Interface' },
        0x08: { 0x00: 'SERCOS Interface Standard (IEC 61491)' },
        0x09: { 0x00: 'CANbus' },
        0x0A: { 0x00: 'MIPI I3CSM Host Controller Interface' },
        0x80: { 0x00: 'Other Serial Bus Controllers' }
    },
    0x0d: {
        0x00: { 0x00: 'iRDA compatible controller' },
        0x01: { 0x00: 'Consumer IR controller',
                0x10: 'UWB Radio controller' },
        0x10: { 0x00: 'RF controller' },
        0x11: { 0x00: 'Bluetooth' },
        0x12: { 0x00: 'Broadband' },
        0x20: { 0x00: 'Ethernet (802.11a – 5 GHz)' },
        0x21: { 0x00: 'Ethernet (802.11b – 2.4 GHz)' },
        0x40: { 0x00: 'Cellular controller/modem' },
        0x41: { 0x00: 'Cellular controller/modem plus Ethernet (802.11)' },
        0x80: { 0x00: 'Other type of wireless controller' }
    },
    0x0e: {
        0x00: 'Intelligent I/O (I2O) Architecture Specification 1.0'
    },
    0x0f: {
        0x01: { 0x00: 'TV' },
        0x02: { 0x00: 'Audio' },
        0x03: { 0x00: 'Voice' },
        0x04: { 0x00: 'Data' },
        0x80: { 0x00: 'Other satellite communication controller' }
    },
    0x10: {
        0x00: { 0x00: 'Network and computing encryption and decryption controller' },
        0x10: { 0x00: 'Entertainment encryption and decryption controller' },
        0x80: { 0x00: 'Other encryption and decryption controller' }
    },
    0x11: {
        0x00: { 0x00: 'DPIO modules' },
        0x01: { 0x00: 'Performance counters' },
        0x10: { 0x00: 'Communications synchronization plus time and frequency test/measurement' },
        0x20: { 0x00: 'Management card' },
        0x80: { 0x00: 'Other data acquisition/signal processing controllers' }
    },
    0x12: {
        0x00: { 0x00: 'Processing Accelerator' }
    },
    0x13: {
        0x00: { 0x00: 'Non-Essential Instrumentation Function' }
    },
    0xff: 'Device does not fit any defined class'
}

class PciHeader:
    def __init__(self, regs):
        self.bars = None
        self.vendor_id = regs[0] & 0xffff
        self.device_id = regs[0] >> 16
        self.command = regs[1] & 0xffff
        self.status = regs[1] >> 16
        self.revision_id = regs[2] & 0xff
        self.prog_if = (regs[2] >> 8) & 0xff
        self.subclass = (regs[2] >> 16) & 0xff
        self.class_code = (regs[2] >> 24) & 0xff
        self.cache_line_size = regs[3] & 0xff
        self.latency_timer = (regs[3] >> 8) & 0xff
        self.header_type = (regs[3] >> 16) & 0xff
        self.bist = (regs[3] >> 24) & 0xff

    def info(self):
        try:
            devclass = devices[self.class_code]

            if isinstance(devclass, str):
                return devclass

            subclass = devclass[self.subclass]

            if isinstance(subclass, str):
                return subclass

            return subclass[self.prog_if]

        except KeyError:
            return 'Unknown'

    def get_header_type(self):
        return self.header_type & 0x7f

class StandardHeader(PciHeader):
    def __init__(self, regs):
        super().__init__(regs)
        self.cardbus_cis_pointer = regs[10]
        self.subsystem_vendor_id = regs[11] & 0xffff
        self.subsystem_id = regs[11] >> 16
        self.expansion_rom_base_address = regs[12]
        self.capabilities_pointer = regs[13] & 0xff
        self.interrupt_line = regs[15] & 0xff
        self.interrupt_pin = (regs[15] >> 8) & 0xff
        self.min_grant = (regs[15] >> 16) & 0xff
        self.max_latency = (regs[15] >> 24) & 0xff

    def reg_nums(self):
        return [4, 6, 8]

class Pci2Pci(PciHeader):
    def __init__(self, regs):
        super().__init__(regs)
        self.primary_bus_number = regs[6] & 0xff
        self.secondary_bus_number = (regs[6] >> 8) & 0xff
        self.subordinate_bus_number = (regs[6] >> 16) & 0xff
        self.secondary_latency_timer = (regs[6] >> 24) & 0xff
        self.io_base = regs[7] & 0xff
        self.io_limit = (regs[7] >> 8) & 0xff
        self.secondary_status = regs[7] >> 16
        self.memory_base = regs[8] & 0xffff
        self.memory_limit = (regs[8] >> 16) & 0xffff
        self.prefetchable_memory_base = regs[9] & 0xffff
        self.prefetchable_memory_limit = (regs[9] >> 16) & 0xffff
        self.prefetechable_base_upper32 = regs[10]
        self.prefetchable_limit_upper32= regs[11]
        self.io_base_upper16 = regs[12] & 0xffff
        self.io_limit_upper16 = (regs[12] >> 16) & 0xffff
        self.capability_pointer = regs[13] & 0xff
        self.expansion_rom_base_address = regs[14]
        self.interrupt_line = regs[15] & 0xff
        self.interrupt_pin = (regs[15] >> 8) & 0xff
        self.bridge_control = regs[15] >> 16

class Cardbus(PciHeader):
    def __init__(self, regs):
        super().__init__(regs)
        self.card_bus_socket_base_address = regs[4]
        self.capabilities_list_offset = regs[5] & 0xff
        self.secondary_status = regs[5] >> 16
        self.pci_bus_number = regs[6] & 0xff
        self.cardbus_number = (regs[6] >> 8) & 0xff
        self.subordinate_bus_number = (regs[6] >> 16) & 0xff
        self.cardbus_latency_timer = (regs[6] >> 24) & 0xff
        self.memory_base_address0 = regs[7]
        self.memory_limit0 = regs[8]
        self.memory_base_address1 = regs[9]
        self.memory_limit1 = regs[10]
        self.io_base_address0 = regs[11]
        self.io_limit0 = regs[12]
        self.io_base_address1 = regs[13]
        self.io_limit1 = regs[14]
        self.interrupt_line = regs[15] & 0xff
        self.interrupt_pin = (regs[15] >> 8) & 0xff
        self.bridge_control = regs[15] >> 16
        self.subsystem_device_id = regs[16] & 0xffff
        self.subsystem_vendor_id = regs[16] >> 16
        self.legacy_mode_base_address = regs[17]

class Bar:
    def __init__(self, reg_num, reg, size, reg_high):
        if reg & 1:
            self.bar = reg & 0xfffffffc
            self.bar_size = (1 + ~(size & ~7)) & 0xffff 
            self.bar_type = 'IO-space'
        else:
            if ((reg >> 1) & 3) == 2:
                self.bar = (reg  & 0xfffffff0) | (reg_high << 32)
                self.bar_size = 1 + ~(size & ~15)
                self.bar_type = 'MEM-space 64-bit'
            else:
                self.bar = reg & 0xfffffff0
                self.bar_size = 1 + ~(size & ~15)
                self.bar_type = 'MEM-space'

class Session(session.Session):
    cache = True
    dump_only = True
    timeout = 0

    def __init__(self, guest_cls):
        super().__init__(guest_cls)
        self.pci = dict()
        self.initialized = False

    def scan_pci(self):
        self.execute(
            f"""{self.context_save()}
                PUT_TP List
                    xor r8, r8
                    pci_read_dev_bus_next:
                    call pci_read_dev_slots
                    inc r8
                    cmp r8, 256
                    jnz pci_read_dev_bus_next
                PUT_TP Nil
                REPLY
                {self.context_restore()}
                pci_read_dev_slots:
                    xor r9, r9
                pci_read_dev_slots_next:
                    call pci_read_dev_funcs
                    inc r9
                    cmp r9, 32
                    jnz pci_read_dev_slots_next
                    ret
                pci_read_dev_funcs:
                    xor r10, r10
                pci_read_dev_funcs_next:
                    call pci_read_dev_regs
                    inc r10
                    cmp r10, 8
                    jnz pci_read_dev_funcs_next
                    ret
                pci_read_dev_regs:
                    xor r11, r11
                    call pci_read
                    cmp eax, 0xffffffff
                    jz pci_read_dev_regs_exit_fail
                    PUT_TP List
                        PUT_VA CString, "bus", UInt16, r8
                        PUT_VA CString, "slot", UInt16, r9
                        PUT_VA CString, "func", UInt16, r10
                        pci_read_dev_regs_next:
                        mov dword [regs+r11*4], eax
                        inc r11
                        cmp r11, 18
                        jz pci_read_dev_regs_exit
                        call pci_read
                        jmp pci_read_dev_regs_next
                        pci_read_dev_regs_exit:
                        PUT_VA CString, "regs", Array, array_h, regs
                    PUT_TP Nil
                pci_read_dev_regs_exit_fail:
                    ret
                pci_read:
                    mov rax, r8
                    shl rax, 5
                    or rax, r9
                    shl rax, 3
                    or rax, r10
                    shl rax, 6
                    or rax, r11
                    shl rax, 2
                    mov rdx, 0x80000000
                    or rax, rdx
                    mov rdx, 0xCF8
                    out dx, eax
                    mov rdx, 0xCFC
                    in eax, dx
                    ret
                array_h: dd 18, UInt32
                regs: dd 18 dup (0)""")

    def inject_read_bar_code(self):
        code = f"""
            read_bar:
                xor rcx, rcx
                call pci_read
                mov rbx, rax
                cmp rax, 1
                jnz mem_space_bar
            bar32:
                mov r12, 0xffffffff
                call pci_write
                call pci_read
                mov rdi, rax
                mov r12, rbx
                call pci_write
                jmp read_bar_out
            mem_space_bar:
                shr rax, 1
                and rax, 3
                cmp rax, 2
                jnz bar32
                inc r11
                call pci_read
                mov rcx, rax
                mov r12, 0xffffffff
                dec r11
                call pci_write
                call pci_read
                mov rdi, rax
                mov r12, rbx
                call pci_write
            read_bar_out:
                PUT_VA UInt32, r11, UInt32, rbx, UInt32, rdi, UInt32, rcx
                ret
            pci_read:
                mov rax, r8
                shl rax, 5
                or rax, r9
                shl rax, 3
                or rax, r10
                shl rax, 6
                or rax, r11
                shl rax, 2
                mov rdx, 0x80000000
                or rax, rdx
                mov rdx, 0xCF8
                out dx, eax
                mov rdx, 0xCFC
                in eax, dx
                ret
            pci_write:
                mov rax, r8
                shl rax, 5
                or rax, r9
                shl rax, 3
                or rax, r10
                shl rax, 6
                or rax, r11
                shl rax, 2
                mov rdx, 0x80000000
                or rax, rdx
                mov rdx, 0xCF8
                out dx, eax
                mov rdx, 0xCFC
                mov rax, r12
                out dx, eax
                ret"""
        self.read_bar_addr = self.guest.op_write(self.code(code))

    def scan_device(self, bus, slot, func, regs):
        if bus not in self.pci.keys():
            self.pci[bus] = dict()

        if slot not in self.pci[bus].keys():
            self.pci[bus][slot] = dict()

        pci = PciHeader(regs)
        pci = {
            0: StandardHeader,
            1: Pci2Pci,
            2: Cardbus
        }[pci.get_header_type()](regs)
        self.pci[bus][slot][func] = pci
        code = ''

        for reg in pci.reg_nums():
            code += f"""
            mov r11, {reg}
            call {self.read_bar_addr:#x}
            """
    
        self.execute(
            f"""{self.context_save()}
                PUT_TP List
                mov r8, {bus}
                mov r9, {slot}
                mov r10, {func}
                {code}
                PUT_TP Nil
                REPLY
                {self.context_restore()}
            """)
        _, bars = self.next_message()
        dev = self.pci[bus][slot][func]
        dev.bars = [Bar(*bar) for bar in bars]

        if self.dump_only:
            self.print_dev_info(bus, slot, func, dev)

    def print_bar_info(self, bar):
        print((f'\t{"BAR " + bar.bar_type : <30}: 0x{bar.bar: <16x} size:{bar.bar_size: #x}'))

    def print_dev_info(self, bus, slot, func, dev):
        print(f'\033[1m{int(bus):02x}:{slot:02x}:{func:02x}: {dev.info()}\033[0m')

        for k, v in dev.__dict__.items():
            if k == 'bars':
                for bar in v:
                    self.print_bar_info(bar)
            else:
                print(f'\t{k: <30}: {v:#x}')

    def on_boot(self, body):
        super().on_boot(body)

        if not self.initialized and self.cache: 
            self.scan_pci()
            self.inject_read_bar_code()

            for args in self.next_message()[1]:
                self.scan_device(**dict(args))
                
            self.initialized = True
            
            if self.dump_only:
                exit(0)
