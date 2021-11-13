#!/bin/sh

/usr/bin/qemu-system-x86_64 \
	-m 64 \
	-kernel bzImage \
	-nographic \
	-append "rw console=ttyS0 nokaslr quiet" \
	-initrd initramfs.cpio \
	-fsdev local,id=fs1,path=/home/kali/GHHv6/ch12/shared,security_model=none \
	-device virtio-9p-pci,fsdev=fs1,mount_tag=host-shared \
	-monitor /dev/null \
	-cpu kvm64,smep,smap \
	-s

