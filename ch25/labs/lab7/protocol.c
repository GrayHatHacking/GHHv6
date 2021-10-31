/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#include "common.h"
#include "protocol.h"

struct msg_buffer {
    unsigned int offset;
    uint8_t buf[MAX_MSGSZ];
};

static struct msg_buffer send_buf;
static struct msg_buffer oob_buf;
static struct msg_buffer recv_buf;

#define PUT(b, v) ({                                          \
    typeof((typeof(v))v) tmp;                                 \
    unsigned int new_offset = b->offset + sizeof(v);          \
    assert(new_offset > b->offset && MAX_MSGSZ > new_offset); \
    *(typeof(tmp) *)&b->buf[b->offset] = v;                   \
    b->offset = new_offset;                                   \
})

#define GET(v) ({                                                   \
    unsigned int new_offset = recv_buf.offset + sizeof(v);          \
    assert(new_offset > recv_buf.offset && MAX_MSGSZ > new_offset); \
    v = *(typeof(v) *)&recv_buf.buf[recv_buf.offset];               \
    recv_buf.offset = new_offset;                                   \
})

void put_tp(bool is_oob, TP prefix) {
    struct msg_buffer *buf = is_oob ? &oob_buf : &send_buf;
    PUT(buf, prefix);
}

TP get_tp() {
    TP prefix;
    GET(prefix);
    return prefix;
}

void put_primitive(bool is_oob, TP prefix, const Primitive_t *value) {
    struct msg_buffer *buf = is_oob ? &oob_buf : &send_buf;
    assert(PrimitiveMax >= prefix);
    put_tp(is_oob, prefix);

    switch (prefix) {
        case UInt8:
            PUT(buf, value->u8);
            break;
        case UInt16:
            PUT(buf, value->u16);
            break;
        case UInt32:
            PUT(buf, value->u32);
            break;
        case UInt64:
            PUT(buf, value->u64);
            break;
        case Int8:
            PUT(buf, value->i8);
            break;
        case Int16:
            PUT(buf, value->i16);
            break;
        case Int32:
            PUT(buf, value->i32);
            break;
        case Int64:
            PUT(buf, value->i64);
            break;
        default:
            assert(false);
    }
}

void get_primitive(TP prefix, Primitive_t *value) {
    assert(PrimitiveMax >= prefix);
    switch (prefix) {
        case UInt8:
            GET(value->u8);
            break;
        case UInt16:
            GET(value->u16);
            break;
        case UInt32:
            GET(value->u32);
            break;
        case UInt64:
            GET(value->u64);
            break;
        case Int8:
            GET(value->i8);
            break;
        case Int16:
            GET(value->i16);
            break;
        case Int32:
            GET(value->i32);
            break;
        case Int64:
            GET(value->i64);
            break;
        default:
            assert(false);
    }
}

void put_array(bool is_oob, const Array_t *array, const void *data) {
    struct msg_buffer *buf = is_oob ? &oob_buf : &send_buf;
    uint32_t len = 0;
    put_tp(is_oob, Array);
    PUT(buf, *array);

    while (array->count * (array->subtype & 0xff) != len)
        PUT(buf, ((const char *)data)[len++]);
}

void get_array(Array_t *array, void **dst_ptr) {
    GET(*array);
    unsigned int offset = recv_buf.offset + array->count * (array->subtype & 0xff);
    assert(offset > recv_buf.offset && MAX_MSGSZ > offset);
    *dst_ptr = &recv_buf.buf[recv_buf.offset];
    recv_buf.offset = offset;
}

void put_cstring(bool is_oob, const char *ptr) {
    struct msg_buffer *buf = is_oob ? &oob_buf : &send_buf;
    put_tp(is_oob, CString);
    do { PUT(buf, *ptr); } while (*ptr++ != '\0');
}

static void _put_va(bool is_oob, TP prefix, va_list args) {
    if (PrimitiveMax >= prefix) {
        Primitive_t value = va_arg(args, Primitive_t);
        put_primitive(is_oob, prefix, &value);
    }

    if (List == prefix) {
        put_tp(is_oob, prefix);
        do {
            prefix = va_arg(args, TP);
            _put_va(is_oob, prefix, args);
        } while (Nil != prefix);
        put_tp(is_oob, prefix);
    }

    if (Array == prefix) {
        Array_t *a = va_arg(args, Array_t *);
        put_array(is_oob, a, va_arg(args, const void *));
    }

    if (CString == prefix)
        put_cstring(is_oob, va_arg(args, const char *));
}

static void _get_va(TP prefix, va_list args) {
    assert(get_tp() == prefix);

    if (PrimitiveMax >= prefix)
        get_primitive(prefix, va_arg(args, void *));

    if (List == prefix)
        do {
            prefix = va_arg(args, TP);
            _get_va(prefix, args);
        } while (Nil != prefix);

    if (Array == prefix) {
        Array_t *a = va_arg(args, Array_t *);
        get_array(a, va_arg(args, void **));
    }

    if (CString == prefix)
        assert(false); /* TODO */
}

void put_va(bool is_oob, ...) {
    va_list ap;
    va_start(ap, is_oob);
    TP prefix = va_arg(ap, TP);
    _put_va(is_oob, prefix, ap);
    va_end(ap);
}

void get_va(TP prefix, ...) {
    va_list ap;
    va_start(ap, prefix);
    _get_va(prefix, ap);
    va_end(ap);
}

void send_msg(MT msg_type) {
    struct msg_buffer *buf = (MTOOB == msg_type) ? &oob_buf : &send_buf;
    MsgHdr hdr = {
        .type = msg_type,
        .len = buf->offset,
        .checksum = crc32(buf->buf, buf->offset),
        .hdr_csum = 0
    };
    hdr.hdr_csum = crc32(&hdr, sizeof(hdr) - sizeof(hdr.hdr_csum));   
    write_serial(&hdr, sizeof(hdr));
    write_serial(buf->buf, buf->offset);
    buf->offset = 0;
}

static bool msg_hdr_valid(const MsgHdr *hdr) {
    return MTRequest == hdr->type && MAX_MSGSZ > hdr->len &&
        crc32(hdr, sizeof(*hdr) - sizeof(hdr->hdr_csum)) == hdr->hdr_csum;
}

void recv_msg() {
    MsgHdr hdr;
    read_serial(&hdr, sizeof(hdr));
    assert(msg_hdr_valid(&hdr));
    recv_buf.offset = 0;
    read_serial(recv_buf.buf, hdr.len);
    assert(crc32(recv_buf.buf, hdr.len) == hdr.checksum);
}

void _reset_oob_buffer() {
    oob_buf.offset = 0;
}
