#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

from subprocess import Popen, PIPE, DEVNULL
import guest

class Guest(guest.Guest):
    debugger = 'gdbserver 127.0.0.1:2345'
    stderr = False

    def __enter__(self):
        self.proc = Popen(
            (f'exec {self.debugger} qemu-system-x86_64 '
            '-display none -boot d -cdrom kernel_bios.iso '
            '-m 300M -serial stdio -enable-kvm '
            '-device usb-ehci,id=ehci '
            '-device usb-mouse,bus=ehci.0'
            ),
            stdin=PIPE, stdout=PIPE,
            stderr={True: None, False: DEVNULL}[self.stderr],
            shell=True
        )
        return self

