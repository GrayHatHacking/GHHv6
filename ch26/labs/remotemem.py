#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

from functools import total_ordering
import bisect
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

    def free_all(self):
        for address in list(self.allocations.keys()):
            self.free(address)


class PageAlloc:
    def __init__(self, mem, data_len):
        self.mem = mem
        self.data_len = data_len & ~0xfff
        
        if data_len & 0xfff:
            self.data_len += 0x1000
            
        self.ptr = self.mem.alloc(self.data_len + 0x1000)

    def start(self):
        return (self.ptr & ~0xfff) + 0x1000

    def end(self):
        return self.start() + self.data_len

    def size(self):
        return self.data_len

    def page_list(self):
        return list(range(self.start(), self.end(), 0x1000))

    def free(self):
        self.mem.free(self.ptr)


@total_ordering
class Chunk:
    def __init__(self, data, offset=None):
        self.data = data
        self.offset = offset

    def __eq__(self, other):
        return self.offset == other.offset

    def __lt__(self, other):
        return self.offset < other.offset


class IOVector:
    def __init__(self, chunk_list=None):
        self.data = []

        if chunk_list is not None:
            for chunk in chunk_list:
                self.append(chunk.data, chunk.offset) 

    def size(self):
        if self.data == []:
            return 0

        last_chunk = self.data[-1] 
        return last_chunk.offset + len(last_chunk.data)

    def append(self, data, offset=None):
        if offset is None:
            offset = self.size()

        bisect.insort(self.data, Chunk(data, offset)) 

    def iter(self):
        return iter(self.data)

