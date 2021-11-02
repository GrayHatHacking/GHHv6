/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#include "common.h"

void kmain() {
    setup_serial();
    write_serial("Hello world!", 12);
    __asm__ __volatile__("hlt");
}
