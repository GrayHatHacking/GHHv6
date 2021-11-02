/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MTBoot = UINT32_C(0),
    MTRequest,
    MTReply,
    MTOOB,
    MTMax = MTOOB
} MT;

#define MAX_MSGSZ UINT32_C(0x400000) /* 4MB */

typedef struct {
    MT type;
    uint32_t len;
    uint32_t checksum; /* body CRC32 */
    uint32_t hdr_csum; /* header CRC32 */
} __attribute__((packed)) MsgHdr;

typedef enum {
    /* primitive sizes encoded in LSB */
    UInt8 = UINT32_C(0x001),
    UInt16 = UINT32_C(0x002),
    UInt32 = UINT32_C(0x004),
    UInt64 = UINT32_C(0x008),
    Int8 = UINT32_C(0x101),
    Int16 = UINT32_C(0x102),
    Int32 = UINT32_C(0x104),
    Int64 = UINT32_C(0x108),
    PrimitiveMax = Int64,
    /* Compound types */
    Array = UINT32_C(0x400),
    CString = UINT32_C(0x500),
    List = UINT32_C(0x600),
    Nil = UINT32_C(0x700)
} TP;

typedef union {
    uint8_t u8;
    uint16_t u16;
    uint32_t u32;
    uint64_t u64;
    int8_t i8;
    int16_t i16;
    int32_t i32;
    int64_t i64;
} Primitive_t;

typedef struct {
    uint32_t count;
    TP subtype;
} __attribute__((packed)) Array_t;

typedef enum {OOBPrint = UINT32_C(0), OOBAssert} OOBType;
typedef enum {OpWrite = UINT32_C(0), OpExec} OpType;

void put_tp(bool is_oob, TP prefix);
TP get_tp();
void put_primitive(bool is_oob, TP prefix, const Primitive_t *value);
void get_primitive(TP prefix, Primitive_t *value);
void put_array(bool is_oob, const Array_t *array, const void *data);
void put_cstring(bool is_oob, const char *ptr);
void put_va(bool is_oob, ...);
void get_va(TP prefix, ...);
void send_msg(MT msg_type);
void recv_msg();

#define LIST(...) List, __VA_ARGS__, Nil
#define PUT_LIST(is_oob, ...) (put_va(is_oob, LIST(__VA_ARGS__)))
#define OOB_PRINT(fmt, ...) ({                                   \
    PUT_LIST(true, UInt32, OOBPrint, CString, fmt, __VA_ARGS__); \
    send_msg(MTOOB);                                             \
})

#endif
