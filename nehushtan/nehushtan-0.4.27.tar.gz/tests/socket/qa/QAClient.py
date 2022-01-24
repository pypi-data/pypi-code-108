import random
import time
from threading import Thread

from nehushtan.socket.NehushtanTCPSocketClient import NehushtanTCPSocketClient


class QAClient(NehushtanTCPSocketClient):
    def handle_client_conneciton(self):
        for i in range(10):
            r = random.Random()
            count = r.randint(2, 5)
            x = []
            for i in range(count):
                x.append(f'{r.randint(10, 20)}')
            x = '+'.join(x)

            print(f'Q: {x}=?')

            self.get_connection().send(x.encode())
            data = self.get_connection().recv(1024)

            print(f'A: {data.decode()}')

            time.sleep(1)

        self.close_connection()


def client_call():
    QAClient(4354).listen()


if __name__ == '__main__':

    for i in range(20):
        Thread(target=client_call).start()
        time.sleep(random.Random().random() * 5)
