;;    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
;;    SPDX-License-Identifier: GPL-3.0-or-later
extern kmain
global _start
[bits 32]
[section .bss]
align 0x1000
resb 0x2000
stack_top:
pd: resb 0x1000 * 4 ; 4 PDs = maps 4GB
pdpt: resb 0x1000   ; 1 PDPT
pml4: resb 0x1000   ; 1 PML
[section .data]
gdt:                  ; minimal 64-bit GDT
dq 0x0000000000000000
dq 0x00A09b000000ffff ; kernel CS
dq 0x00C093000000ffff ; kernel DS
gdt_end:              ; TODO: TSS
gdtr:
dw gdt_end - gdt - 1  ; GDT limit
dq gdt                ; GDT base
[section .text]
align 8, db 0
;; multiboot2 header
mb_header_size equ (mb_header_end - mb_header)
mb_header:
dd 0xE85250D6     ; magic field
dd 0              ; architecture field: i386 32-bit protected-mode 
dd mb_header_size ; header length field
dd 0xffffffff & -(0xE85250D6 + mb_header_size) ; checksum field
;; termination tag
dw 0 ; tag type
dw 0 ; tag flags
dd 8 ; tag size
mb_header_end:
;; kernel code starts here
_start:
mov esp, stack_top
mov edi, pd
mov ecx, 512*4
mov eax, 0x87
init_pde:
mov dword [edi], eax
add eax, 0x200000
add edi, 8
dec ecx
jnz init_pde
mov dword [pdpt], pd + 7
mov dword [pdpt+0x08], pd + 0x1007
mov dword [pdpt+0x10], pd + 0x2007
mov dword [pdpt+0x18], pd + 0x3007
mov eax, pml4
mov dword [eax], pdpt + 7
mov cr3, eax        ; load page-tables
mov ecx, 0xC0000080
rdmsr
or eax, 0x101       ; LME | SCE 
wrmsr               ; set EFER
lgdt [gdtr]         ; load 64-bit GDT
mov eax, 0x1ba      ; PVI | DE | PSE | PAE | PGE | PCE
mov cr4, eax
mov eax, 0x8000003b ; PG | PE | MP | TS | ET | NE
mov cr0, eax
jmp 0x08:code64
[bits 64]
code64:
mov ax, 0x10
mov ds, ax
mov es, ax
mov ss, ax
call kmain
