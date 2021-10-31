/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#ifndef COMMON_H
#define COMMON_H
#include <stdint.h>

#define va_start(v,l) __builtin_va_start(v,l)
#define va_arg(v,l) __builtin_va_arg(v,l)
#define va_end(v) __builtin_va_end(v)
typedef __builtin_va_list va_list;

void setup_serial();
void write_serial(const void *data, unsigned long len);
void read_serial(void *data, unsigned long len);
uint32_t crc32(const void *data, unsigned long len);
void reset();
void __assert(const char *msg, const char *file, int line);
#define assert(EX) (void)((EX) || (__assert(#EX, __FILE__, __LINE__),0))

#endif
