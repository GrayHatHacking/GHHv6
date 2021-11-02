/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#ifndef COMMON_H
#define COMMON_H
#include <stdint.h>

void setup_serial();
void write_serial(const void *data, unsigned long len);
void read_serial(void *data, unsigned long len);

#endif
