#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import construct as c
import fixedint as f
from crc32c import crc32c

MT = c.Enum(c.Int32ul, Boot=0, Request=1, Reply=2, OOB=3)
MAX_MSGSZ = 0x400000
MsgHdr = c.Struct(
    'hdr' / c.RawCopy(
        c.Struct(
            'type'         / MT,
            'len'          / c.ExprValidator(c.Int32ul, c.obj_ <= MAX_MSGSZ),
            '_csum_offset' / c.Tell,
            'checksum'     / c.Int32ul
        )
    ),
    'hdr_csum' / c.Checksum(c.Int32ul, crc32c, c.this.hdr.data)
)
TP = c.Enum(c.Int32ul,
    UInt8=0x001, UInt16=0x002, UInt32=0x004, UInt64=0x008,
    Int8=0x101, Int16=0x102, Int32=0x104, Int64=0x108,
    Array=0x400, CString=0x500, List=0x600, Nil=0x700
)
IntPrefixes = (
    TP.UInt8, TP.UInt16, TP.UInt32, TP.UInt64,
    TP.Int8, TP.Int16, TP.Int32, TP.Int64
)
IntConstructs = (
    c.Int8ul, c.Int16ul, c.Int32ul, c.Int64ul,
    c.Int8sl, c.Int16sl, c.Int32sl, c.Int64sl
)
IntFixed = (
    f.UInt8, f.UInt16, f.UInt32, f.UInt64, f.Int8, f.Int16, f.Int32, f.Int64
)

def make_adapter(cInt, fInt):
    return c.ExprSymmetricAdapter(cInt, lambda obj, _: fInt(obj))

IntAdapters = (
    make_adapter(cInt, fInt) for cInt, fInt in zip(IntConstructs, IntFixed)
)
IntAlist = list(zip(IntPrefixes, IntAdapters))

class ArrayAdapter(c.Adapter):
    def _decode(self, obj, context, path):
        subtype = dict(zip(IntPrefixes, IntFixed))[obj.subtype]
        return tuple(subtype(x) for x in obj.v)

    def _encode(self, obj, context, path):
        subtype = dict(zip(IntFixed, IntPrefixes))[type(obj[0])]
        return {'count': len(obj), 'subtype': subtype, 'v': obj}

class ListAdapter(c.Adapter):
    def _decode(self, obj, context, path):
        ret = []

        while obj.head != None:
            ret.append(obj.head)
            obj = obj.tail
        
        return ret

    def _encode(self, obj, context, path):
        xs = {'head': None, 'tail': None}

        for x in reversed(obj):
            xs = {'head': x, 'tail': xs}

        return xs

List = c.Struct(
    'head' / c.LazyBound(lambda: Body),
    'tail' / c.If(c.this.head != None, c.LazyBound(lambda: List))
)
CompAlist = [
    (TP.Array, ArrayAdapter(
        c.Struct(
            'count'   / c.Int32ul,
            'subtype' / c.Select(*(c.Const(x, TP) for x in IntPrefixes)),
            'v'       / c.Array(
                c.this.count, c.Switch(c.this.subtype, dict(IntAlist)))))),
    (TP.CString, c.CString('ascii')),
    (TP.List, ListAdapter(List)),
    (TP.Nil, c.Computed(None))
]

PythonObj = IntFixed + (tuple, str, list, type(None))
Prefixes = IntPrefixes + (TP.Array, TP.CString, TP.List, TP.Nil)

class BodyAdapter(c.Adapter):
    def _decode(self, obj, context, path):
        return obj.value

    def _encode(self, obj, context, path):
        return {
            'prefix': dict(zip(PythonObj, Prefixes))[type(obj)],
            'value': obj
        }

Body = BodyAdapter(
    c.Struct(
        'prefix' / TP,
        'value'  / c.Switch(c.this.prefix, dict(IntAlist + CompAlist)))
)
Message = c.Struct(
    'header'         / MsgHdr,
    'body'           / c.RawCopy(Body),
    '_body_checksum' / c.Pointer(
        c.this.header.hdr.value._csum_offset,
        c.Checksum(c.Int32ul, crc32c, c.this.body.data)
    )
)

def recv(reader):
    hdr = reader.read(MsgHdr.sizeof())
    body = reader.read(MsgHdr.parse(hdr).hdr.value.len)
    msg = Message.parse(hdr + body)
    return (msg.header.hdr.value.type, msg.body.value)

def send(writer, body):
    body = Body.build(body)
    header = MsgHdr.build({
        'hdr': {
            'value': {
                'type': MT.Request,
                'len': len(body),
                'checksum': crc32c(body)
            }
        }
    })
    writer.write(header + body)
    writer.flush()
