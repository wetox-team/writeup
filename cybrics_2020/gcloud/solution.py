#!/usr/bin/env python3

# todo: wireshark -> copy all items as data.json

import os
import binascii

def solve():
    nonascii_bytes = []
    unique_nonascii_bytes = []
    definitely_unique_nonascii_bytes = []

    assert os.path.exists('data.json'), 'Export items from wireshark to data.json file'

    os.system("cat data.json | grep data.data | tr -d ' \t,:\"' > data")

    with open('data', 'r') as file:
        data = file.read().replace('data.data', '').split('\n')

    data = [binascii.unhexlify(d) for d in data]

    for d in data:
        try:
            d.decode('utf-8')
        except:
            nonascii_bytes.append(d)

    for d in nonascii_bytes:
        if d not in unique_nonascii_bytes:
            unique_nonascii_bytes.append(d)

    for i, d in enumerate(unique_nonascii_bytes):
        if i == 0:
            if unique_nonascii_bytes[1].startswith(d):
                continue
        elif (i == len(unique_nonascii_bytes) - 1):
            if unique_nonascii_bytes[i-1].endswith(d):
                continue
        else:
            if unique_nonascii_bytes[i+1].startswith(d) or unique_nonascii_bytes[i-1].endswith(d):
                continue
        definitely_unique_nonascii_bytes.append(d)

    jpg_bytes = b''.join(definitely_unique_nonascii_bytes[1:])

    with open('flag.jpg', 'wb') as file:
        file.write(jpg_bytes)

    print('Solved, check flag.jpg file')


if __name__ == '__main__':
    solve()
