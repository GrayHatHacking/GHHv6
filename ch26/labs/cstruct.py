#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import math
import construct as c


class CStruct(c.Struct):
    def __init__(self, *subcons):
        subcons = list(subcons)
        offset = 0
        largest_align = min(8, subcons[0].sizeof())
        
        for i, subcon in enumerate(subcons):
            # assume all are c.Renamed
            name = subcon.name
            subcon = subcon.subcon
            subcon._offset = offset
            
            if i+1 < len(subcons):
                next_subcon = subcons[i+1].subcon

                while isinstance(next_subcon, c.Array):
                    next_subcon = next_subcon.subcon 

                if isinstance(next_subcon, c.Bytes):
                    align = 1
                else:
                    if isinstance(next_subcon, c.Struct):
                        align = next_subcon._largest_align
                    else:
                        align = next_subcon.sizeof()

                largest_align = max(align, largest_align)
            else:
                align = min(8, largest_align)
            
            self._largest_align = align
            offset = align * math.ceil((offset + subcon.sizeof())/align)
            padding = offset - subcon._offset
            new_subcon = c.Padded(padding, subcon)
            new_subcon._offset = subcon._offset
            subcons[i] = name / new_subcon

        super().__init__(*subcons)
