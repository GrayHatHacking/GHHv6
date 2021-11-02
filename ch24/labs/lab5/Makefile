CFLAGS = -march=native -std=gnu99 -Wall -nostdlib -nostartfiles -nodefaultlibs -fno-stack-protector -mno-red-zone
MKRESCUE = /usr/bin/grub-mkrescue
GRUB_EFI_FLAGS = -d /usr/lib/grub/x86_64-efi/
GRUB_BIOS_FLAGS = -d /usr/lib/grub/i386-pc/
OBJECTS = main.o bootstrap.o common.o protocol.o

all: kernel_efi.iso kernel_bios.iso

%.o : %.c
	$(CC) $(CFLAGS) -c $< -o $@

bootstrap.o : bootstrap.asm
	nasm -felf64 $< -o $@

kernel_efi.iso: iso/boot/kernel
	$(MKRESCUE) $(GRUB_EFI_FLAGS) -o $@ iso

kernel_bios.iso: iso/boot/kernel 
	$(MKRESCUE) $(GRUB_BIOS_FLAGS) -o $@ iso

iso/boot/kernel: $(OBJECTS)
	$(LD) -melf_x86_64 $^ -o $@

clean:
	rm -f *.o iso/boot/kernel *.iso

