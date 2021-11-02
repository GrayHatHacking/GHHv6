;;    SPDX-FileCopyrightText: 2021 Daniel Fernandez Kuehr <daniel.kuehr@tacitosecurity.com>
;;    SPDX-License-Identifier: GPL-3.0-or-later
%macro arg_wrap 2
  %ifnidn %1, %2
    %ifstr %1
      jmp %%endstr
      %%str: db %1, 0
      %ifidni %2, stack
        %%endstr: push %%str
      %else
        %%endstr: mov %2, %%str
      %endif
    %else
      %ifidni %2, stack
        push %1
      %else
        mov %2, %1
      %endif
    %endif
  %endif
%endmacro

%macro multipush 1-*
  %rep %0
    arg_wrap %1, stack
    %rotate 1
  %endrep
%endmacro

;; At the cost of more emmited code this macro clobbers registers
;; WARNING this clobbers rdx even for functions returning 128-bit values
%macro sysvcall 1-* rdi, rsi, rdx, rcx, r8, r9
  multipush r11, r10, r9, r8, rcx, rdx, rsi, rdi

  %if %0 >= 8
    multipush %{-1:8}
    %assign stack_offset ((%0 - 7) * 8)
  %else
    %assign stack_offset 0
  %endif

  %if %0 >= 2
    arg_wrap %2, rdi
  %endif

  %if %0 >= 3
    %ifidn %3, rdi
      arg_wrap qword [rsp+stack_offset], rsi
    %else
      arg_wrap %3, rsi
    %endif
  %endif

  %if %0 >= 4
    %ifidni %4, rdi
      arg_wrap qword [rsp+stack_offset], rdx
    %elifidn %4, rsi
      arg_wrap qword [rsp+stack_offset+8], rdx
    %else
      arg_wrap %4, rdx
    %endif
  %endif

  %if %0 >= 5
    %ifidni %5, rdi
      arg_wrap qword [rsp+stack_offset], rcx
    %elifidn %5, rsi
      arg_wrap qword [rsp+stack_offset+8], rcx
    %elifidn %5, rdx
      arg_wrap qword [rsp+stack_offset+0x10], rcx
    %else
      arg_wrap %5, rcx
    %endif
  %endif

  %if %0 >= 6
    %ifidni %6, rdi
      arg_wrap qword [rsp+stack_offset], r8
    %elifidn %6, rsi
      arg_wrap qword [rsp+stack_offset+8], r8
    %elifidn %6, rdx
      arg_wrap qword [rsp+stack_offset+0x10], r8
    %elifidn %6, rcx
      arg_wrap qword [rsp+stack_offset+0x18], r8
    %else
      arg_wrap %6, r8
    %endif
  %endif

  %if %0 >= 7
    %ifidni %7, rdi
      arg_wrap qword [rsp+stack_offset], r9
    %elifidn %7, rsi
      arg_wrap qword [rsp+stack_offset+8], r9
    %elifidn %7, rdx
      arg_wrap qword [rsp+stack_offset+0x10], r9
    %elifidn %7, rcx
      arg_wrap qword [rsp+stack_offset+0x18], r9
    %elifidn %7, r8
      arg_wrap qword [rsp+stack_offset+0x20], r9
    %else
      arg_wrap %7, r9
    %endif
  %endif

  xor rax, rax
  call %1

  %if %0 > 7
    add rsp, (%0 - 7)*8
  %endif

  pop rdi
  pop rsi
  pop rdx
  pop rcx
  pop r8
  pop r9
  pop r10
  pop r11
%endmacro

UInt8 equ 0x001
UInt16 equ 0x002
UInt32 equ 0x004
UInt64 equ 0x008
Int8 equ 0x101
Int16 equ 0x102
Int32 equ 0x104
Int64 equ 0x108
Array equ 0x400
CString equ 0x500
List equ 0x600
Nil equ 0x700

MTReply equ 2
MTOOB equ 3

%macro OOB_PRINT 1+
  sysvcall put_va, 1, List, UInt32, 0, CString, %1, Nil
  sysvcall send_msg, MTOOB
%endmacro

%macro REPLY 0
  sysvcall send_msg, MTReply
%endmacro

%macro REPLY_EMPTY 0
  sysvcall put_va, 0, List, Nil
  REPLY
%endmacro

%macro PUT_VA 1+
  sysvcall put_va, 0, List, %1, Nil
%endmacro

%macro PUT_TP 1
  sysvcall put_tp, 0, %1
%endmacro

%macro PUT_STRING 1
  sysvcall put_cstring, 0, %1
%endmacro

