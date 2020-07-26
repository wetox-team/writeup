XCorp (Network)

Author: Artur Khanov ([@awengar](https://t.me/awengar))

We got into the XCorp network and captured some traffic from an employee's machine. 
Looks like they were using some in-house software that keeps their secrets.

[src](./xcorp.tar.gz)

---

## Solution

1. Find the transfer package of the largest file \[[net10.exe](./net10.exe)\]

2. Run the program, enter username (often appears in requests)

Flag is [here](./flag.jpg) 
