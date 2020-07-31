#!/usr/bin/env python3

import base64
import binascii
import string

h = binascii.hexlify
b = base64.b64encode

c = b'37151032694744553d12220a0f584315517477520e2b3c226b5b1e150f5549120e5540230202360f0d20220a376c0067'
base64_alph = string.ascii_letters + string.digits + '+/='


def enc(f):
    e = b(f)
    z = []
    i = 0
    while i < len(e):
        z += [ e[i] ^ e[((i + 1) % len(e))]]
        i = i + 1
    c = h(bytearray(z))
    return c


def _dec(c, char):
    z = binascii.unhexlify(c)
    f = char + '*' * (int(len(z) / 4) * 3)
    e = bytearray(base64.b64encode(f.encode()))
    for i in range(len(z) - 1):
         e[i+1] = e[i] ^ z[i]
    f = base64.b64decode(e)
    return f


def dec(c):
    results = []
    for char in base64_alph:
        try:
            r = _dec(c, char)
        except:
            pass
        if r not in results:
            print(r)
        results.append(r)
    return results


def cli():
    action = input('Enter action [enc/dec]: ')
    value = input('Enter value: ').encode()
    print('\n')
    if action == 'enc':
        print(enc(value).decode())
    elif action == 'dec':
        dec(value)


def solve():
    dec(c)


if __name__ == '__main__':
    print(solve())
