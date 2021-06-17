#include "common.h"

void kmain() {
    setup_serial();
    write_serial("Hello world!", 12);
    __asm__ __volatile__("hlt");
}
