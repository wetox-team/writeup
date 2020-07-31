## Tyrannosaurus Rex [Cryptography] 

We found this fossil. Can you reverse time and bring this back to life?

[src](./fossil)

---

## Solution

**How to work enc function:**

1. Encode string to base64

2. Create a new string from the encoded one by applying xor to each character: 

    `new [i] = base64_encoded [i] ^ base64_encoded [i + 1]` 

3. Convert the result to hex

**How to work decode:**

1. Convert the hex string to bytes (`binascii.unhexlify`)

2. Know first char
    
    1. If you don't know it just repeat algorithm for each base64 alphabet's chars

3. `base64_encoded [i + 1] = base64_encoded [i] ^ new [i]` 

solution script: [solution.py](./solution.py)

flag is `flag{tyrannosauras_xor_in_reverse}`
