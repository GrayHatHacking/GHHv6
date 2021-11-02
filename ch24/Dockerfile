FROM kalilinux/kali-rolling
COPY ./labs /labs
RUN apt update
RUN apt install -y build-essential nasm bsdmainutils
RUN apt install -y grub-pc-bin grub-efi-amd64-bin xorriso mtools
RUN apt install -y python3 pip
RUN apt-get install -y qemu-kvm 
RUN pip install construct fixedint crc32c portion

