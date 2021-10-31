/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#include <stdint.h>
#include "multiboot2.h"
#include "protocol.h"
#include "common.h"

extern char __ehdr_start, _end; 

static void put_symbols() {
    PUT_LIST(false, CString, "symbols",
            LIST(SYMBOL(__ehdr_start),
                 SYMBOL(_end),
                 SYMBOL(put_tp),
                 SYMBOL(put_array),
                 SYMBOL(put_cstring),
                 SYMBOL(put_va),
                 SYMBOL(send_msg)));
}

static void put_mmap(const struct multiboot_tag_mmap *mmap) {
    const struct multiboot_mmap_entry *entry, *end;
    end = PTR_ADD(&mmap->entries[0], mmap->size - sizeof(*mmap));
    put_tp(false, List);

    for (entry = &mmap->entries[0]; entry != end;
        entry = PTR_ADD(entry, mmap->entry_size))
        PUT_LIST(false,
            NAMED("address", UInt64, entry->addr),
            NAMED("length", UInt64, entry->len),
            NAMED("type", UInt32, entry->type));

    put_tp(false, Nil);
}

static void put_mbi(const void *mbi) {
    const struct multiboot_tag *tag;    

    for (tag = PTR_ADD(mbi, ALIGN_UP(sizeof(uint64_t), MULTIBOOT_TAG_ALIGN));
        tag->type != MULTIBOOT_TAG_TYPE_END;
        tag = PTR_ADD(tag, ALIGN_UP(tag->size, MULTIBOOT_TAG_ALIGN))) {
        /* OOB_PRINT("multiboot tag 0x%08x", UInt32, tag->type); */
        switch (tag->type) {
            case MULTIBOOT_TAG_TYPE_MMAP:
                put_tp(false, List);
                put_cstring(false, "mmap");
                put_mmap((const struct multiboot_tag_mmap *)tag);
                put_tp(false, Nil);
                break;
            /* TODO: handle other tags */
            default:
                break;
        }
    }
}

static void op_write() {
    Primitive_t addr;
    Array_t array;
    uint8_t *payload;
    get_va(UInt64, &addr);
    get_va(Array, &array, &payload);

    for (uint32_t x = 0; x != array.count * (array.subtype & 0xff); x += 1)
        ((uint8_t *)addr.u64)[x] = payload[x];
}

static void op_exec() {
    Primitive_t addr;
    get_va(UInt64, &addr);
    ((void (*)())addr.u64)();
}

void kmain(const void *mbi) {
    setup_serial();
    OOB_PRINT("kmain at 0x%016lx", UInt64, &kmain);
    put_tp(false, List);
    put_symbols();
    put_mbi(mbi);
    put_tp(false, Nil);
    send_msg(MTBoot);

    while (1) {
        recv_msg();
        assert(List == get_tp());

        for (TP prefix = get_tp(); Nil != prefix; prefix = get_tp()) {
            Primitive_t op_type;

            assert(UInt32 == prefix); /* requests must start with ReqType */
            get_primitive(prefix, &op_type);
            assert(OpWrite == op_type.u32 || OpExec == op_type.u32);

            if (OpWrite == op_type.u32)
                op_write();

            if (OpExec == op_type.u32)
                op_exec();
        }
    }
}
