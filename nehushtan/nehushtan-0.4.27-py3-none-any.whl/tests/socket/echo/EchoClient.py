from nehushtan.socket.NehushtanTCPSocketClient import NehushtanTCPSocketClient


class EchoClient(NehushtanTCPSocketClient):

    def handle_client_conneciton(self):
        connection = self.get_connection()

        while True:
            x = input("Say: ")
            if not x:
                break

            sent = connection.send(x.encode())
            print(f'[DEBUG] handle_client_conneciton sent bytes: {sent}')
            received = connection.recv(1024)
            print(f'Heard from {connection.getpeername()}: {received}')

        self.close_connection()


if __name__ == '__main__':
    EchoClient(4444).listen()
