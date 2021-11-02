FROM kalilinux/kali-rolling
COPY ./labs /labs
RUN apt update
RUN apt install -y build-essential nasm bsdmainutils git gdb gdbserver pkg-config curl colordiff jq
RUN apt install -y grub-pc-bin grub-efi-amd64-bin xorriso mtools
RUN apt install -y python3 pip
RUN pip install construct fixedint crc32c portion pwntools
RUN apt install -y libpixman-1-dev libglib2.0-dev
RUN /bin/bash -c "git clone --depth 1 --branch v5.1.0-rc3 https://github.com/qemu/qemu.git && mkdir qemu/build && cd qemu/build && ../configure --target-list=x86_64-softmmu --enable-debug --disable-strip && make && make install"
RUN /bin/bash -c "cd /labs && make"

