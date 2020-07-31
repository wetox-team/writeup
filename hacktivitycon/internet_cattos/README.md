## InternetCattos [Warmups]

The Internet is full of wonderful kittens and cattos. 
You can even find one at jh2i.com on port 50003!

---

## Solution

```python
import socket, time

sock = socket.socket()
sock.connect(('jh2i.com', 50003))
time.sleep(1)
data = sock.recv(1024).replace(b'\r', b'').decode()
print(data)
```

solution script: [solution.py](./solution.py)

flag is `flag{this_netcat_says_meow}`
