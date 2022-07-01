// leak-bof.c
#include <stdio.h>
#include <unistd.h>

void vuln() {
    char buff[128];
    printf("Overflows with 128 bytes: ");
    fflush(stdout);
    read(0, buff, 2000);
}

int main(int argc, char **argv) {
    printf("I'm leaking printf: %p\n", (long)printf);
    vuln();
}

