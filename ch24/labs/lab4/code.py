#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import os
from subprocess import run
from tempfile import NamedTemporaryFile

class Code:
    def __init__(self, code, sym):
        self.code = '[bits 64]\n'
        self.code += '\n'.join(f'{k} equ {v:#x}' for (k, v) in sym.items())
        self.code += '\n%include "macros.asm"\n' + code

    def build(self, base_address):
        with NamedTemporaryFile('w') as f:
            f.write(f'[org {base_address:#x}]\n' + self.code)
            f.flush()
            run(f'nasm -fbin -o {f.name}.bin {f.name}', shell=True)
    
            with open(f'{f.name}.bin', 'rb') as fout:
                ret = fout.read()

            os.remove(f'{f.name}.bin')

        return ret
