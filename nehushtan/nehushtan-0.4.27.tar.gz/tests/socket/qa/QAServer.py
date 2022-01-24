import os
import socket
import time
from threading import Thread, Event

from nehushtan.socket.NehushtanTCPSocketServer import NehushtanTCPSocketServer


class SampleEvent(Event):
    pass


event = SampleEvent()


class QAServer(NehushtanTCPSocketServer):
    def handle_incoming_connection(self, connection: socket.socket, address):
        # peer = connection.getpeername()

        event.set()

        try:
            while True:
                # print(f'[DEBUG] recv-ing from {peer}')
                buffer = connection.recv(1024)
                # print(f'[DEBUG] recv-ed from {peer}: {buffer}')

                if not buffer:
                    # print(f'[FATAL] recv empty so connection might be closed')
                    break

                parts = buffer.split(b'+')
                s = 0
                for part in parts:
                    if part:
                        s += int(part.decode())
                connection.send(f'{s}'.encode())
        except ConnectionResetError as e:
            # print(f'[WARN] ConnectionResetError by peer [{peer}]: {e}')
            pass

        # print(f'[DEBUG] finished with {peer}')


def with_monitor_fork():
    main_pid = os.getpid()
    child_pid = os.fork()
    if child_pid == 0:
        # I am the child
        for i in range(60):
            print(f'[MONITOR] <{i}> total threads: {server.get_thread_manager().check_alive_thread_count()}')
            time.sleep(1)

        print('[MONITOR] OVER')
    else:
        # Main
        server.listen()


def with_monitor_thread(server: NehushtanTCPSocketServer):
    thread = Thread(target=monitor_thread_worker, args=(server,))
    thread.start()


def monitor_thread_worker(server: NehushtanTCPSocketServer):
    while event.wait():
        print(f'[MONITOR] total threads: {server.get_thread_manager().check_alive_thread_count()}')
        event.clear()

    print('[MONITOR] OVER')


if __name__ == '__main__':
    server = QAServer(4354)

    with_monitor_thread(server)

    server.listen()
