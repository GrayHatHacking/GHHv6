#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import uuid
import hypercall
import construct as c
from remotemem import PageAlloc
from enum import Enum
from math import ceil


class VmbusChannelMessage(Enum):
    INVALID = 0
    OFFERCHANNEL = 1
    RESCIND_CHANNELOFFER = 2
    REQUESTOFFERS = 3
    ALLOFFERS_DELIVERED = 4
    OPENCHANNEL = 5
    OPENCHANNEL_RESULT = 6
    CLOSECHANNEL = 7
    GPADL_HEADER = 8
    GPADL_BODY = 9
    GPADL_CREATED = 10
    GPADL_TEARDOWN = 11
    GPADL_TORNDOWN = 12
    RELID_RELEASED = 13
    INITIATE_CONTACT = 14
    VERSION_RESPONSE = 15
    UNLOAD = 16
    UNLOAD_RESPONSE = 17
    TL_CONNECT_REQUEST = 21

VmbusChannelMessageHeader = c.Struct(
    'msgtype' / c.Int32ul,
    'padding' / c.Const(0, c.Int32ul)
)

VmbusChannelInitiateContact = c.Struct(
    'hdr' / VmbusChannelMessageHeader,
    'vmbus_version_requested' / c.Int32ul,
    'target_vcpu'   / c.Int32ul,
    'msg_sint'      / c.Int8ul,
    'padding'       / c.Bytes(7),
    'monitor_page1' / c.Int64ul,
    'monitor_page2' / c.Int64ul
)

VmbusChannelVersionResponse = c.Struct(
    'hdr' / VmbusChannelMessageHeader,
    'version_supported' / c.Int8ul,
    'connection_state'  / c.Int8ul,
    'padding'           / c.Int16ul,
    'msg_conn_id'       / c.Int32ul
)

class UUIDAdapter(c.Adapter):
    def _decode(self, obj, context, path):
        return uuid.UUID(bytes_le=obj)        

    def _encode(self, obj, context, path):
        return obj.bytes_le

UUID = UUIDAdapter(c.Bytes(16))

vmbus_devices = {
    uuid.UUID('{f8615163-df3e-46c5-913f-f2d2f965ed0e}'):
        'Network',  
    uuid.UUID('{32412632-86cb-44a2-9b5c-50d1417354f5}'):
        'IDE', 
    uuid.UUID('{ba6163d9-04a1-4d29-b605-72e2ffb1dc7f}'):
        'SCSI',
    uuid.UUID('{0e0b6031-5213-4934-818b-38d90ced39db}'):
        'Shutdown',  
    uuid.UUID('{9527E630-D0AE-497b-ADCE-E80AB0175CAF}'):
        'Time Synch', 
    uuid.UUID('{57164f39-9115-4e78-ab55-382f3bd5422d}'):
        'Heartbeat', 
    uuid.UUID('{a9a0f4e7-5a45-4d96-b827-8a841e8c03e6}'):
        'KVP', 
    uuid.UUID('{525074dc-8985-46e2-8057-a307dc18a502}'):
        'Dynamic memory', 
    uuid.UUID('{cfa8b69e-5b4a-4cc0-b98b-8ba1a1f3f95a}'):
        'Mouse', 
    uuid.UUID('{f912ad6d-2b17-48ea-bd65-f927a61c7684}'):
        'Keyboard', 
    uuid.UUID('{35fa2e29-ea23-4236-96ae-3a6ebacba440}'):
        'VSS (Backup/Restore)', 
    uuid.UUID('{DA0A7802-E377-4aac-8E77-0558EB1073F8}'):
        'Synthetic Video', 
    uuid.UUID('{2f9bcc4a-0069-4af3-b76b-6fd0be528cda}'):
        'Synthetic FC', 
    uuid.UUID('{34D14BE3-DEE4-41c8-9AE7-6B174977C192}'):
        'Guest File Copy Service', 
    uuid.UUID('{8c2eaf3d-32a7-4b09-ab99-bd1f1c86b501}'):
        'NetworkDirect', 
    uuid.UUID('{44C4F61D-4444-4400-9D52-802E27EDE19F}'):
        'PCI Express Pass Through', 
    uuid.UUID('{f8e65716-3cb3-4a06-9a60-1889c5cccab5}'):
        'Automatic Virtual Machine Activation', 
    uuid.UUID('{3375baf4-9e15-4b30-b765-67acb10d607b}'):
        'Automatic Virtual Machine Activation (2)',
    uuid.UUID('{276aacf4-ac15-426c-98dd-7521ad3f01fe}'):
        'Remote Desktop Virtualization' 
}

VmbusChannelOffer = c.Struct(
    'if_type'           / UUID,
    'if_instance'       / UUID,
    'reserved1'         / c.Int64ul,
    'reserved2'         / c.Int64ul,
    'chn_flags'         / c.Int16ul,
    'mmio_megabytes'    / c.Int16ul,
    'user_def'          / c.Bytes(120),
    'sub_channel_index' / c.Int16ul,
    'reserved3'         / c.Int16ul
)

VmbusChannelOfferChannel = c.Struct(
    'hdr'                    / VmbusChannelMessageHeader,
    'offer'                  / VmbusChannelOffer,
    'child_relid'            / c.Int32ul,
    'monitorid'              / c.Int8ul,
    'monitor_allocated'      / c.Int8ul,
    'is_dedicated_interrupt' / c.Int16ul,
    'connection_id'          / c.Int32ul
)

GPARange = c.Struct(
    'byte_count'  / c.Int32ul,
    'byte_offset' / c.Int32ul,
    'pfn_array'   / c.Array(
        lambda t: ceil((t.byte_count + t.byte_offset) / 4096), c.Int64ul)
)

def gpa_range(address, size):
    start_pfn = address >> 12
    end_pfn = (address + size) >> 12 
    return {
        'byte_count': size,
        'byte_offset': address & 0xfff,
        'pfn_array': range(start_pfn, end_pfn)
    }

def gpa_range_size(range_list):
    return len(b''.join(map(GPARange.build, range_list)))

VmbusChannelGPADLHeader = c.Struct(
    'hdr'          / VmbusChannelMessageHeader,
    'child_relid'  / c.Int32ul,
    'gpadl'        / c.Int32ul,
    'range_buflen' / c.Rebuild(c.Int16ul, lambda t: gpa_range_size(t.range)),
    'rangecount'   / c.Rebuild(c.Int16ul, c.len_(c.this.range)),
    'range'        / c.Array(c.this.rangecount, GPARange),
)

VmbusChannelGPADLBody = c.Struct(
    'hdr'       / VmbusChannelMessageHeader,
    'msgnumber' / c.Int32ul,
    'gpadl'     / c.Int32ul
)

VmbusChannelGPADLCreated = c.Struct(
    'hdr'             / VmbusChannelMessageHeader,
    'child_relid'     / c.Int32ul,
    'gpadl'           / c.Int32ul,
    'creation_status' / c.Int32ul
)

VmbusChannelOpenChannel = c.Struct(
    'hdr'               / VmbusChannelMessageHeader,
    'child_relid'       / c.Int32ul,
    'openid'            / c.Int32ul,
    'ringbuffer_gpadl'  / c.Int32ul,
    'target_vp'         / c.Int32ul,
    'downstream_offset' / c.Int32ul,
    'user_data'         / c.Bytes(120),
)

VmbusChannelOpenResult = c.Struct(
    'hdr'         / VmbusChannelMessageHeader,
    'child_relid' / c.Int32ul,
    'openid'      / c.Int32ul,
    'status'      / c.Int32ul,
)

RingBuffer = c.Struct(
    'write_index'     / c.Int32ul,
    'read_index'      / c.Int32ul,
    'interrupt_mask'  / c.Int32ul,
    'pending_send_sz' / c.Int32ul,
    'reserved'        / c.Bytes(48),
    'feature_bits'    / c.Int32ul
)

class PacketType(Enum):
    VM_PKT_INVALID = 0
    VM_PKT_SYNCH = 1
    VM_PKT_ADD_XFER_PAGESET = 2
    VM_PKT_RM_XFER_PAGESET = 3
    VM_PKT_ESTABLISH_GPADL = 4
    VM_PKT_TEARDOWN_GPADL = 5
    VM_PKT_DATA_INBAND = 6
    VM_PKT_DATA_USING_XFER_PAGES = 7
    VM_PKT_DATA_USING_GPADL = 8
    VM_PKT_DATA_USING_GPA_DIRECT = 9
    VM_PKT_CANCEL_REQUEST = 10
    VM_PKT_COMP = 11
    VM_PKT_DATA_USING_ADDITIONAL_PKT = 12
    VM_PKT_ADDITIONAL_DATA = 13

PacketHeader = c.Struct(
    'type'     / c.Int16ul,
    'offset8'  / c.Int16ul,
    'len8'     / c.Int16ul,
    'flags'    / c.Int16ul,
    'trans_id' / c.Int64ul
)

VMBUS_PKT_TRAILER = 8


class Session(hypercall.Session):
    list_offers = False

    def synic_init(self):
        """
        NOTE: we assign SINT2 to vector 32 but our IDT doesn't have it,
        however, this is not a problem as we set the SINT in polling mode.
        (Also interrupts are disabled)

        If interrupts were enabled and the polling bit wasn't set, things
        would break badly. To avoid it, install_idt, and make_vector_handler
        should be overloaded.

        In case of install_idt just to enlarge the IDT for example:

            def install_idt(self, vectors=33):
                super().install_idt(vectors)

        In case of make_vector_handler custom assembly should be generated to
        vector 32 so it can deal with SINT2 delivery. 
        """
        code = self.code(
            f"""
            {self.context_save()}
            xor rdx, rdx
            ;; map SIMP
            mov rcx, 0x40000083; HV_X64_MSR_SIMP
            mov rax, {self.synic_simp | 1:#x}
            wrmsr
            ;; unmask SINT2 and set to vector 32
            mov rcx, 0x40000092; HV_X64_MSR_SINT2
            mov rax, 32 | 1 << 18; polling mode
            wrmsr
            ;; enable SynIC
            mov rcx, 0x40000080; HV_X64_MSR_SCONTROL
            mov rax, 1
            wrmsr
            {self.context_restore()}
            """)
        self.guest.execute(code)

    def synic_read_simp(self, SINT):
        msg_size = hypercall.HvMessage.sizeof()
        msg_slot_addr = self.synic_simp + msg_size * SINT
        data_buf = self.guest.memory.alloc(msg_size)
        code = self.code(
            f"""
            {self.context_save()}
            mov rsi, {msg_slot_addr:#x}
            ;; is slot empty?
            cmp dword [rsi], 0
            jz fallout
            ;; copy message
            mov rdi, {data_buf:#x}
            mov rcx, {msg_size}
            rep movsb
            ;; let know the hypervisor that we are done
            mov dword [{msg_slot_addr:#x}], 0
            mov rcx, 0x40000084 ; HV_X64_MSR_EOM
            xor rdx, rdx
            xor rax, rax
            wrmsr            				
            fallout:
            ;; send message to the client
            PUT_VA Array, array_h, {data_buf:#x}
            REPLY
            {self.context_restore()}
            array_h: dd {msg_size}, UInt8
            """)
        self.guest.execute(code)
        self.guest.memory.free(data_buf)
        _, result = self.next_message()
        msg = hypercall.HvMessage.parse(bytes(result[0]))

        if msg.Header.MessageType == 0:
            return None

        return msg.Payload

    def synic_poll_simp(self, SINT):
        msg = None

        while msg is None:
            msg = self.synic_read_simp(SINT)

        return msg

    def vmbus_handle_message(self, msg):
        hdr_size = VmbusChannelMessageHeader.sizeof()
        hdr = VmbusChannelMessageHeader.parse(msg[:hdr_size])
        msgtype = VmbusChannelMessage(hdr.msgtype)
        handler = {
            VmbusChannelMessage.VERSION_RESPONSE:
                self.vmbus_handle_version_response,
            VmbusChannelMessage.OFFERCHANNEL:
                self.vmbus_handle_offer,
            VmbusChannelMessage.ALLOFFERS_DELIVERED:
                self.vmbus_handle_offers_delivered,
            VmbusChannelMessage.GPADL_CREATED:
                self.vmbus_handle_gpadl_created,
            VmbusChannelMessage.OPENCHANNEL_RESULT:
                self.vmbus_handle_open_result
        }[msgtype]
        return handler(msg)

    def vmbus_read_message(self):
        return self.vmbus_handle_message(self.synic_poll_simp(SINT=2))

    def vmbus_initiate_contact(self):
        VERSION_WIN10_V5 = 5 << 16
        payload = VmbusChannelInitiateContact.build({
            'hdr': { 'msgtype': VmbusChannelMessage.INITIATE_CONTACT.value },
            'vmbus_version_requested': VERSION_WIN10_V5,
            'target_vcpu': 0,
            'msg_sint': 2,
            'padding': bytes(7),
            'monitor_page1': self.monitor_page1,
            'monitor_page2': self.monitor_page2
        })

        if self.HvCallPostMessage(self.connection_id, 1, payload) != 0:
            print(f'VMBus initiate contact failed')
            exit(1)

        if self.vmbus_read_message() != 0:
            print('VMBus version negotiation error')
            exit(1)

    def vmbus_handle_version_response(self, msg):
        msg = VmbusChannelVersionResponse.parse(msg)

        if msg.version_supported == 0:
            return -1

        self.connection_id = msg.msg_conn_id
        return 0

    def vmbus_request_offers(self):
        payload = VmbusChannelMessageHeader.build({
            'msgtype': VmbusChannelMessage.REQUESTOFFERS.value
        })
        
        if self.HvCallPostMessage(self.connection_id, 1, payload) != 0:
            print('VMBus request offers failed')
            exit(1)
                
        while not self.all_offers_delivered:
            self.vmbus_read_message()

    def vmbus_handle_offer(self, msg):
        msg = VmbusChannelOfferChannel.parse(msg)
        self.offers.append(msg)

        if self.list_offers:
            if msg.offer.if_type in vmbus_devices.keys():
                dev_type = vmbus_devices[msg.offer.if_type]
            else:
                dev_type = f'Unknown UUID {msg.offer.if_type}'

            print(f'[OFFER ID: {msg.child_relid}] {msg.offer.if_instance} {dev_type}')

    def vmbus_handle_offers_delivered(self, msg):
        self.all_offers_delivered = True
        return 0
    
    def vmbus_create_gpadl(self, child_relid, address, size):
        self.gpadl = (self.gpadl + 1) & 0xffffffff
        payload = VmbusChannelGPADLHeader.build({
            'hdr': { 'msgtype': VmbusChannelMessage.GPADL_HEADER.value },
            'child_relid': child_relid,
            'gpadl': self.gpadl,
            'range': [gpa_range(address, size)]
        })
        chunk_size = hypercall.HV_MESSAGE_PAYLOAD_BYTE_COUNT
        # For some odd reason the "range" field is 4-byte aligned, breaking
        # the 8-byte alignment of PFNs, so we need this ugly -4 hack. 
        header = payload[:chunk_size-4]
        body = payload[chunk_size-4:]
        
        if self.HvCallPostMessage(self.connection_id, 1, header) != 0:
            print('VMBus Send GPADL header failed')
            exit(1)

        chunk_size -= VmbusChannelGPADLBody.sizeof()
        chunks = (body[x:x + chunk_size]
            for x in range(0, len(body), chunk_size))

        for n, chunk in enumerate(chunks):
            payload = VmbusChannelGPADLBody.build({
                'hdr': { 'msgtype': VmbusChannelMessage.GPADL_BODY.value },
                'msgnumber': n,
                'gpadl': self.gpadl,
            }) + chunk

            if self.HvCallPostMessage(self.connection_id, 1, payload) != 0:
                print(f'VMBus Send GPADL body ({n}) failed')
                exit(1)

        if self.vmbus_read_message() == 0 \
            and child_relid in self.gpadls.keys() \
            and self.gpadls[child_relid] == self.gpadl:
            self.gpadls[child_relid] = (self.gpadl, address, size)
        else:
            print(f'VMBus GPADL creation failed')
            exit(1)      

    def vmbus_handle_gpadl_created(self, msg):
        msg = VmbusChannelGPADLCreated.parse(msg)
        self.gpadls[msg.child_relid] = msg.gpadl
        return msg.creation_status

    def vmbus_open_channel(self, child_relid):
        self.openid = (self.openid + 1) & 0xffffffff
        gpadl, address, size = self.gpadls[child_relid]
        downstream_offset = (size >> 2) >> 12 # split ringbuffer in half
        self.ringbuffer_init(child_relid, address, size, downstream_offset)   
        payload = VmbusChannelOpenChannel.build({
            'hdr': { 'msgtype': VmbusChannelMessage.OPENCHANNEL.value },
            'child_relid': child_relid,
            'openid': self.openid,
            'ringbuffer_gpadl': gpadl,
            'target_vp': 0,
            'downstream_offset': downstream_offset,
            'user_data': bytes(120)
        })
        
        if self.HvCallPostMessage(self.connection_id, 1, payload) != 0 \
            or self.vmbus_read_message() != 0:
            print('VMBus open channel failed')
            exit(1)

    def vmbus_handle_open_result(self, msg):
        msg = VmbusChannelOpenResult.parse(msg)
        return msg.status

    def vmbus_device_open(self, if_instance=None, if_type=None, ring_size=0x40000):
        def device_open(offer, ring_size):
            address = PageAlloc(self.guest.memory, ring_size).start()
            self.vmbus_create_gpadl(offer.child_relid, address, ring_size)
            self.vmbus_open_channel(offer.child_relid)
            return offer.child_relid

        for offer in self.offers:
            if if_instance is not None:
                if offer.offer.if_instance == if_instance:
                    return device_open(offer, ring_size)
            elif if_type is not None:
                if offer.offer.if_type == if_type:
                    return device_open(offer, ring_size)
        raise

    def vmbus_init(self):
        self.connection_id = 4
        self.offers = []
        self.all_offers_delivered = False
        self.gpadl = 0
        self.gpadls = dict()
        self.openid = 0
        self.ringbuffer = dict()
        self.vmbus_initiate_contact()
        self.vmbus_request_offers()

    def ringbuffer_init(self, child_relid, address, size, offset_pages):
        upstream = (address, offset_pages << 12)
        downstream = (upstream[0] + upstream[1], size - upstream[1])
        self.ringbuffer[child_relid] = [upstream, downstream, 0]
        init_hdr = RingBuffer.build({
            'write_index': 0,
            'read_index': 0,
            'interrupt_mask': 0,
            'pending_send_sz': 0,
            'reserved': bytes(48),
            'feature_bits': 1
        })
        self.guest.op_write_data(init_hdr, upstream[0])
        self.guest.op_write_data(init_hdr, downstream[0])

    def ringbuffer_write(self, ring_buffer, data):
        # WARNING: we assume non-concurrent access, and qword aligned data
        rb_addr, rb_size = ring_buffer
        rb_data_addr = rb_addr + 0x1000
        data_addr = self.guest.op_write_data(data)
        data_len = len(data)
        code = self.code(
            f"""
            {self.context_save()}
            mov edx, dword [{rb_addr:#x}]   ; write_index
            mov ebx, dword [{rb_addr+4:#x}] ; read_index
            mov eax, edx
            xor eax, ebx
            not eax
            mov dword [ring_empty], eax
            mov ecx, {rb_size}
            sub ecx, edx
            add ecx, ebx
            mov eax, ebx
            sub eax, edx
            cmp edx, ebx
            cmovae eax, ecx                 ; wrap around
            mov ecx, {data_len}
            cmp eax, ecx                    
            jb fail                         ; remaining < data len
            mov rsi, {data_addr:#x}
            xor rbx, rbx
            copy:
            cmp rdx, {rb_size}
            cmovae rdx, rbx                 ; wrap around
            mov rax, qword [rsi]
            mov qword [{rb_data_addr:#x}+rdx], rax
            add rdx, 8
            add rsi, 8
            sub rcx, 8
            jnz copy
            mov dword [{rb_addr:#x}], edx   ; update write_index
            xor rax, rax
            exit:
            mov edx, dword [ring_empty]
            PUT_VA UInt64, rax, UInt32, rdx
            REPLY
            {self.context_restore()}
            fail:
            mov rax, -1
            jmp exit
            ring_empty: dd 0
            """)
        self.guest.execute(code)
        self.guest.memory.free(data_addr)
        _, result = self.next_message()
        return result

    def get_connection_id(self, child_relid):
        for offer in self.offers:
            if offer.child_relid == child_relid:
                return offer.connection_id

        raise

    def ringbuffer_send_packet(self, child_relid, packet_type, data, trans_id=None, flags=0):
        upstream, _, _trans_id = self.ringbuffer[child_relid]

        if trans_id is None:
            trans_id = _trans_id

        offset8 = ceil(PacketHeader.sizeof() / 8)
        data_len8 = ceil(len(data) / 8)
        data = data.ljust(data_len8 << 3, b'\0')
        hdr = PacketHeader.build({
            'type': packet_type.value,
            'offset8': offset8,
            'len8': offset8 + data_len8,
            'flags': flags,
            'trans_id': trans_id
        }).ljust(offset8 << 3, b'\0')
        packet = hdr + data + bytes(VMBUS_PKT_TRAILER)
        ret, needs_signal = self.ringbuffer_write(upstream, packet)

        if ret == 0:
            self.ringbuffer[child_relid][2] = (trans_id + 1) & ((1 << 64) - 1)

            if needs_signal:
                connection_id = self.get_connection_id(child_relid)

                if self.HvCallSignalEvent(connection_id, 0) != 0:
                    print('ringbuffer_send_packet: SignalEvent failed')
        
        return ret

    def ringbuffer_read(self, ring_buffer, data_len, update_index=True):
        # WARNING: we assume non-concurrent access, and qword aligned data
        rb_addr, rb_size = ring_buffer
        rb_data_addr = rb_addr + 0x1000
        data_addr = self.guest.memory.alloc(data_len)

        if update_index is True:
            update_index_code = f'mov dword [{rb_addr+4:#x}], edx'
        else:
            update_index_code = ''

        code = self.code(
            f"""
            {self.context_save()}
            mov edx, dword [{rb_addr:#x}]   ; write_index
            mov ebx, dword [{rb_addr+4:#x}] ; read_index
            mov ecx, {rb_size}
            sub ecx, ebx
            add ecx, edx
            mov eax, edx
            sub eax, ebx
            cmp ebx, edx
            cmova eax, ecx                  ; wrap around
            mov ecx, {data_len}
            cmp eax, ecx                    
            jb fail                         ; remaining < data len
            mov rdx, rbx
            xor rbx, rbx
            mov rdi, {data_addr:#x}
            copy:
            cmp rdx, {rb_size}
            cmovae rdx, rbx                 ; wrap around
            mov rax, qword [{rb_data_addr}+rdx]
            mov qword [rdi], rax
            add rdx, 8
            add rdi, 8
            sub rcx, 8
            jnz copy
            {update_index_code}
            PUT_VA Array, array_h, {data_addr:#x}
            REPLY
            exit:
            {self.context_restore()}
            fail:
            REPLY_EMPTY
            jmp exit
            array_h: dd {data_len}, UInt8 
            """)
        self.guest.execute(code)
        self.guest.memory.free(data_addr)
        _, result = self.next_message()

        if result == []:
            return None

        return bytes(result[0])

    def ringbuffer_recv_packet(self, child_relid):
        hdr_len = PacketHeader.sizeof()
        _, downstream, _ = self.ringbuffer[child_relid]
        data = self.ringbuffer_read(downstream, hdr_len, update_index=False)

        if data is None:
            return None

        packet_len = (PacketHeader.parse(data).len8 << 3) + VMBUS_PKT_TRAILER
        return self.ringbuffer_read(downstream, packet_len)

    def on_boot(self, body):
        super().on_boot(body)
        pages = PageAlloc(self.guest.memory, 0x3000).page_list()
        (
            self.synic_simp,
            self.monitor_page1,
            self.monitor_page2
        ) = pages
        self.synic_init()
        self.vmbus_init()
        
        if self.list_offers:
            exit(0)

if __name__ == "__main__":
    Session.list_offers = True
    Session().run()
