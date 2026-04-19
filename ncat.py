# Neocat Viewer

The Neocat viewer is a simple command-line tool for viewing the contents of network sockets using nc (netcat). It provides a user-friendly interface for monitoring and controlling socket connections. Below is the full code for the Neocat viewer.

```python
import socket
import sys

class NeocatViewer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f'Connected to {self.host}:{self.port}')
        except Exception as e:
            print(f'Error connecting: {e}')
            sys.exit(1)

    def receive_data(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    break
                print(data.decode())
        except Exception as e:
            print(f'Error receiving data: {e}')
        finally:
            self.sock.close()

    def run(self):
        self.connect()
        self.receive_data()

if __name__ == '__main__':
    viewer = NeocatViewer(host='localhost', port=8080)
    viewer.run()
```

# How to Use
1. Run the script as follows: `python ncat.py`
2. Modify the `host` and `port` arguments according to your requirements.

# Requirements
- Python 3.x
- Socket library (included in standard Python libraries)

# This code is provided as-is without warranty or guarantee.