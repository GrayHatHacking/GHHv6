#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import uuid
import vmbus
import construct as c
from enum import Enum
from time import ctime

VmbusPipeHeader = c.Struct(
    'flags'   / c.Int32ul,
    'msgsize' / c.Int32ul
)

ICVersion = c.Struct(
    'major' / c.Int16ul,
    'minor' / c.Int16ul
)

class ICMessageType(Enum):
    NEGOTIATE = 0
    HEARTBEAT = 1
    KVPEXCHANGE = 2
    SHUTDOWN = 3
    TIMESYNC = 4
    VSS = 5

ICMSGHDRFLAG_TRANSACTION = 1
ICMSGHDRFLAG_REQUEST = 2
ICMSGHDRFLAG_RESPONSE = 4
WLTIMEDELTA = 116444736000000000
              
ICMessageHeader = c.Struct(
    'icverframe'       / ICVersion,
    'icmsgtype'        / c.Int16ul,
    'icvermsg'         / ICVersion,
    'icmsgsize'        / c.Int16ul,
    'status'           / c.Int32ul,
    'ictransaction_id' / c.Int8ul,
    'icflags'          / c.Int8ul,
    'reserved'         / c.Bytes(2)
)

ICMessageNegotiate = c.Struct(
	'icframe_vercnt' / c.Int16ul,
	'icmsg_vercnt'   / c.Int16ul,
	'reserved'       / c.Const(0, c.Int32ul),
    'icversion_data' / c.Array(
        c.this.icframe_vercnt + c.this.icmsg_vercnt, ICVersion
    )
)

ICTimeSyncRefData = c.Struct(
	'parenttime'      / c.Int64ul,
	'vmreferencetime' / c.Int64ul,
	'flags'           / c.Int8ul,
	'leapflags'       / c.Int8ul,
	'stratum'         / c.Int8ul,
	'reserved'        / c.Bytes(3)
)

ICMessage = c.Struct(
    'pipe_hdr' / VmbusPipeHeader,
    'ic_hdr'   / ICMessageHeader,
    'icmsg'    / c.Switch(c.this.ic_hdr.icmsgtype, {
        ICMessageType.NEGOTIATE.value: ICMessageNegotiate,
        ICMessageType.TIMESYNC.value: ICTimeSyncRefData
        # TODO: implement other IC messages  
    })
)

Packet = c.Struct(
    'packet_hdr' / vmbus.PacketHeader,
    '_start'     / c.Seek(c.this.packet_hdr.offset8 * 8),
    'data'       / ICMessage
)

class Session(vmbus.Session):
    def negotiate(self, msg):
        if msg.ic_hdr.icmsgtype != ICMessageType.NEGOTIATE.value:
            print(f'Recevied unknown IC message {msg.ic_hdr.icmsgtype}')
            exit(1)

        ts_version = None
        # TODO: add support for older versions
        for version in msg.icmsg.icversion_data[:msg.icmsg.icframe_vercnt]:
            if version.major == 3 and version.minor == 0:
                ts_version = version
                break

        if ts_version is None:
            print(f'Unsupported version')
            exit(1)

        icmsg_ver = msg.icmsg.icversion_data[-1]
        msg.icmsg = {
            'icframe_vercnt': 1,
            'icmsg_vercnt': 1,
            'icversion_data': [ts_version, icmsg_ver]
        }
        msg.ic_hdr.icmsgsize = len(ICMessageNegotiate.build(msg.icmsg))
        msg.ic_hdr.icflags = ICMSGHDRFLAG_RESPONSE | ICMSGHDRFLAG_TRANSACTION
        msg.pipe_hdr.msgsize = ICMessageHeader.sizeof() + msg.ic_hdr.icmsgsize
        return ICMessage.build(msg)

    def on_boot(self, body):
        super().on_boot(body)
        time_sync = uuid.UUID('{9527E630-D0AE-497b-ADCE-E80AB0175CAF}')
        child_relid = self.vmbus_device_open(if_type=time_sync)
        packet = Packet.parse(self.ringbuffer_recv_packet(child_relid))
        self.ringbuffer_send_packet(
            child_relid,
            vmbus.PacketType.VM_PKT_DATA_INBAND,
            self.negotiate(packet.data),
            packet.packet_hdr.trans_id
        )
        pkg = self.ringbuffer_recv_packet(child_relid)
        packet = Packet.parse(pkg)
        host_ns = ((packet.data.icmsg.parenttime - WLTIMEDELTA) * 100)
        print(f'Reported Host time: {ctime(host_ns / 1e9)}')
        exit(0)

if __name__ == "__main__":
    Session().run()

