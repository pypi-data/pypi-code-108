import socket
import time

from nehushtan.socket.NehushtanTCPSocketServer import NehushtanTCPSocketServer


class EchoServer(NehushtanTCPSocketServer):
    def should_terminate(self) -> bool:
        return False

    def handle_incoming_connection(self, connection: socket.socket, address):
        print(f'[DEBUG] handle_incoming_connection start for {address}')

        peer = connection.getpeername()
        try:
            while True:
                received = connection.recv(1024)
                if not received:
                    print(f'[FATAL] connection received empty from {peer} may be closed')
                    break

                print(f'{connection.getpeername()}: {received}')

                connection.send(received)
                time.sleep(2)
        except ConnectionResetError as e:
            print(f'[ERROR] ConnectionResetError with {peer}: {e}')


if __name__ == '__main__':
    EchoServer(4444).listen()
