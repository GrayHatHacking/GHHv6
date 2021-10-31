/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#include <stdint.h>
#include <stdbool.h>
#include <x86intrin.h>
#include "protocol.h"

static uint16_t SerialPort = 0x3f8; /* TODO: set it dynamically */

static void outb(uint16_t port, uint8_t val) {
    __asm__ __volatile__("outb %0, %1" :: "a"(val), "Nd"(port));
}

static uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ __volatile__("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

void setup_serial() {
    outb(SerialPort + 1, 0x00); /* disable interrupts */
    outb(SerialPort + 3, 0x80); /* enable DLAB */
    outb(SerialPort + 0, 0x01); /* divisor low = 1 (115200 baud) */
    outb(SerialPort + 1, 0x00); /* divisor high = 0 */
    outb(SerialPort + 3, 0x03); /* 8-bit, no parity, 1 stop bit */
    outb(SerialPort + 2, 0xC7); /* FIFO, clear, 14-byte threshold */
    outb(SerialPort + 4, 0x03); /* DTR/RTS */
}

void write_serial(const void *data, unsigned long len) {
    const uint8_t *ptr = data;        
    while (len) {
        if (!(inb(SerialPort + 5) & 0x20))
            continue;
        len -= 1;
        outb(SerialPort, *ptr++);
    }
}

void read_serial(void *data, unsigned long len) {
    uint8_t *ptr = data;
    while (len) {
        if (!(inb(SerialPort + 5) & 1))
            continue; /* TODO: yield CPU */
        len -= 1;
        *ptr++ = inb(SerialPort);
    }
}

/* TODO: portable implementation supporting older CPUs */
uint32_t crc32(const void *data, unsigned long len) {
    const uint8_t *ptr = data;
    uint32_t ret = 0xffffffff;

    while (len--)
        ret = _mm_crc32_u8(ret, *ptr++);

    return ret ^ 0xffffffff;
}

void reset() {
    struct {
        uint16_t limit;
        unsigned long base;
    } __attribute__((packed)) idtr = {0};

    /* Hard-reset by triple-fault */
    __asm__ __volatile__(
        "lidt %0\n"
        "int $1" :: "m" (idtr));
}

void _reset_oob_buffer();

void __assert(const char *msg, const char *file, int line) {
    _reset_oob_buffer();
    PUT_LIST(true, UInt32, OOBAssert, CString,
            msg, CString, file, Int32, line
    );
    send_msg(MTOOB);
    reset();
}
