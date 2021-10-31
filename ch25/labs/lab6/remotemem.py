#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import portion as P

class RemoteMemoryError(Exception):
    pass

class RemoteMemory:
    def __init__(self):
        self.mem = P.empty()
        self.allocations = dict()

    def add_region(self, base, size):
        interval = P.openclosed(base, base + size)
        self.mem |= interval
        return interval

    def del_region(self, base, size):
        interval = P.openclosed(base, base + size)
        self.mem -= interval
        return interval

    def alloc(self, size):
        for interval in self.mem:
            if interval.upper - interval.lower >= size:
                allocation = self.del_region(interval.lower, size)
                self.allocations[allocation.lower] = allocation
                return allocation.lower

        raise RemoteMemoryError('out of memory')

    def free(self, address):
        self.mem |= self.allocations[address]
        del self.allocations[address]
