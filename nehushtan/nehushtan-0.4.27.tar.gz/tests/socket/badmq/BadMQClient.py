from typing import Optional

from nehushtan.socket.NehushtanUDPSocketClient import NehushtanUDPSocketClient
from tests.socket.badmq.MQCommand import MQCommand


class BadMQClient(NehushtanUDPSocketClient):

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.__command: Optional[MQCommand] = None

    def handle_communication(self):
        sent = self.get_socket_instance().sendto(self.__command.package_as_bytes(), self.get_server_address())
        print(f'[DEBUG] sent to {self.get_server_address()}, {sent} bytes: {self.__command.package_as_bytes()}')

        data = self.get_socket_instance().recv(1024)
        self.__command = MQCommand.parse(data)
        if not self.__command:
            print(f'[WARN] RESULT CANNOT BE PARSED: {data}')
        else:
            print(f'[INFO] RESULT: {self.__command.package_as_bytes()}')

    def dequeue(self):
        self.__command = MQCommand(MQCommand.COMMAND_DEQUEUE, 'QueueA')
        self.handle_communication()
        if self.__command:
            return self.__command.value
        else:
            raise IOError('pop failed')

    def enqueue(self, x: str):
        self.__command = MQCommand(MQCommand.COMMAND_ENQUEUE, 'QueueA', x)
        self.handle_communication()
        if self.__command:
            return self.__command.value
        else:
            raise IOError('pop failed')


if __name__ == '__main__':
    x = BadMQClient('127.0.0.1', 6767)
    print('enqueue 1:', x.enqueue('1'))
    print('enqueue 2:', x.enqueue('2'))
    print('enqueue 3:', x.enqueue('3'))
    print('dequeue (1)', x.dequeue())
    print('dequeue (2)', x.dequeue())
    print('dequeue (3)', x.dequeue())
    print('dequeue (?)', x.dequeue())
