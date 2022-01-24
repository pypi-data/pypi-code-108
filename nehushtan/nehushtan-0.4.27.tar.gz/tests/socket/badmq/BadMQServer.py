from nehushtan.MessageQueue.implement.NehushtanMemoryMessageQueue import NehushtanMemoryMessageQueue
from nehushtan.socket.NehushtanUDPSocketServer import NehushtanUDPSocketServer
from tests.socket.badmq.MQCommand import MQCommand


class BadMQServer(NehushtanUDPSocketServer):

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self.__mq = NehushtanMemoryMessageQueue()

    def handle_incoming_data(self, data: bytes, address):
        print(f'RECV: {data}')
        x = MQCommand.parse(data)
        if x:
            if x.command == MQCommand.COMMAND_DEQUEUE:
                x.value = self.__mq.dequeue(x.queue_name)
                response = x.package_as_bytes()
            elif x.command == MQCommand.COMMAND_ENQUEUE:
                x.value = self.__mq.enqueue(x.value, x.queue_name)
                response = x.package_as_bytes()
            else:
                response = '{"ERROR":"UNKNOWN COMMAND"}'.encode()
        else:
            response = '{"ERROR":"FORMAT ERROR"}'.encode()

        print(f"SEND: {response}")
        self.get_socket_instance().sendto(response, address)


if __name__ == '__main__':
    BadMQServer('127.0.0.1', 6767).listen()
