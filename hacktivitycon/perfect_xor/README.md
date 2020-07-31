## Perfect XOR [Cryptography]

Can you decrypt the flag?
Download the file below.

[src](./decrypt.py)

---

## Solution

1. Check first 3-4 n value

2. Google it

3. It's perfect numbers ([wiki](https://en.wikipedia.org/wiki/Perfect_number))

4. Find first 14 perfect numbers in the internet ([perfect numbers list](https://web.archive.org/web/20090503154707/http://amicable.homepage.dk/perfect.htm))

5. `plain_text[i] == cipher[i] ^ perfect_number[i]`

solution script: [solution.py](./solution.py)

flag is `flag{tHE_br0kEN_Xor}` 
