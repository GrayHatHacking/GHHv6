/*
    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
    SPDX-License-Identifier: GPL-3.0-or-later
*/
#include <stdint.h>

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
