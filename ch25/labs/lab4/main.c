#include <stdint.h>
#include "multiboot2.h"
#include "protocol.h"
#include "common.h"

#define PTR_ADD(a, s) ((typeof(a))((unsigned long)a + s))
#define ALIGN_UP(a, s) ((a + (typeof(a))s - 1) & ~((typeof(a))s - 1))
#define NAMED(n, t, v) LIST(CString, n, t, v)
#define SYMBOL(n) NAMED(#n, UInt64, &n)
extern char __ehdr_start, _end; 

static void put_symbols() {
    PUT_LIST(false, CString, "symbols",
            LIST(SYMBOL(__ehdr_start),
                 SYMBOL(_end),
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

void kmain(const void *mbi) {
    setup_serial();
    OOB_PRINT("kmain at 0x%016lx", UInt64, &kmain);
    put_tp(false, List);
    put_symbols();
    put_mbi(mbi);
    put_tp(false, Nil);
    send_msg(MTBoot);
    __asm__ __volatile__("hlt");
}