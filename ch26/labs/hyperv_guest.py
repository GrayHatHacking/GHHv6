#    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
#    SPDX-License-Identifier: GPL-3.0-or-later

import socket
import guest
from pypsrp.client import Client

host = 'hyperv_box'
proxy_port = 2345
user = 'Administrator'
password = 'password123'
deploy = True
vm_name = 'test_vm'
pipe_name = f'\\\\.\\pipe\\{vm_name}'
create_gen1 = (
    f'Remove-VM -Name {vm_name} -Force; '
    f'New-VM -Name {vm_name} -Generation 1 -MemoryStartupBytes 300MB -BootDevice CD; '
    f'Set-VMDvdDrive -VMName {vm_name} -Path C:\\\\kernel_bios.iso; '
    f'Set-VMComPort -VMName {vm_name} -Number 1 -Path {pipe_name}'
)
create_gen2 = (
    f'Remove-VM -Name {vm_name} -Force; '
    f'New-VM -Name {vm_name} -Generation 2 -MemoryStartupBytes 300MB -BootDevice CD; '
    f'Set-VMDvdDrive -VMName {vm_name} -Path C:\\\\kernel_efi.iso; '
    f'Set-VMFirmware -VMName {vm_name} -EnableSecureBoot Off; '
    f'Set-VMComPort -VMName {vm_name} -Number 1 -Path {pipe_name}'
)

def wsclient():
    return Client(
        host,
        username=user,
        password=password,
        ssl=False,
        auth='basic',
        encryption='never'
    )

class PseudoProc:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, proxy_port))
        self.returncode = None
        self.stdin = self.stdout = self.sock.makefile(mode='rwb')

    def kill(self):
        self.sock.close()
        self.returncode = 1

class Guest(guest.Guest):
    created = False
    create_cmd = create_gen1

    def __enter__(self):
        with wsclient() as client:
            if not Guest.created:
                if deploy:
                    for src_file in ('namedpipe_proxy.exe', 'kernel_bios.iso', 'kernel_efi.iso'):
                        print(f'Copying \033[1m{src_file}\033[0m to remote host...')
                        client.copy(src_file, f'C:\\\\{src_file}')

                print('Creating VM...')
                _, streams, errors = client.execute_ps(self.create_cmd)

                if errors:
                    print('Error(s) creating VM')

                    for err in streams.error:
                        print(str(err))

                    exit(1)

                Guest.created = True
            
            print('Starting VM...')
            _, streams, errors = client.execute_ps((
                f'Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c C:\\\\namedpipe_proxy.exe {pipe_name} > C:\\\\namedpipe_proxy.txt"; '
                f'Start-VM -VMName {vm_name}; '
                'while (!(Get-NetTCPConnection -LocalPort 2345)) { Start-Sleep 1 }'
            ))

            if errors:
                print('Error(s) starting VM')

                for err in streams.error:
                    print(str(err))

                raise

            print('Connecting...')
            self.proc = PseudoProc()
            return self

    def __exit__(self, type, value, traceback):
        self.proc.kill()
        self.proc = None

        with wsclient() as client:
            print('Stopping VM...')
            _, streams, errors = client.execute_ps(f'Stop-VM -Name {vm_name} -Force -TurnOff')

            if errors:
                print('Error(s) stopping VM')

                for err in streams.error:
                    print(str(err))

class GuestGen1(Guest):
    pass

class GuestGen2(Guest):
    create_cmd = create_gen2
