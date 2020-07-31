import socket
import time


def solve():
    sock = socket.socket()
    sock.connect(('jh2i.com', 50003))
    time.sleep(1)
    data = sock.recv(1024).replace(b'\r', b'').decode()
    return data


if __name__ == '__main__':
    print(solve())
