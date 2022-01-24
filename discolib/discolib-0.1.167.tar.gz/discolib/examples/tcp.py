from discolib.core import Disco
from discolib.io import DiscoIO, Validate
import socket

disco = None

class TcpIO(DiscoIO):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 31415))
    _buffer = []

    @Validate.read
    def read_raw(self) -> bytes:
        """Read bytes from the TCP server."""
        while True:
            data = self.sock.recv(1024)
            print(data)
            if not data:
                return b''
            for i, b in enumerate(data):
                print(i, b)
                if b == 0:  # Delimeter!
                    packet = bytes(self._buffer)
                    self._buffer = list(data[i+1:])  # Skip delim.
                    return packet
                self._buffer.append(b)

    @Validate.write
    def write_raw(self, data: bytes) -> None:
        """Send bytes to the TCP server."""
        self.sock.sendall(data)

def main():
    global disco
    disco = Disco(TcpIO())
    print(disco.get_attr_json(indent=2))
    print(dir(disco))

if __name__ == '__main__':
    main()
