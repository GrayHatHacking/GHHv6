//heapme_demo.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void *x[8];

int main() {
    for (int i=0; i < 8; i++) {
        x[i] = malloc(0x38);
        memset(x[i], (i + 0x30), 0x38);
    }

    for (int i=0; i < 8; i++)
        free(x[i]);

    fprintf(stderr, "Press CTRL+C to exit.\n");
    pause();
    return 0;
}

