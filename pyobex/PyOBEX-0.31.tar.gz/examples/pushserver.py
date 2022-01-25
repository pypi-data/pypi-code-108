#!/usr/bin/env python3

import os
import sys

from PyOBEX import headers, responses, server


class PushServer(server.PushServer):

    def __init__(self, address, directory):

        server.PushServer.__init__(self, address)
        self.directory = directory

    def put(self, socket, request):

        name = ""
        body = b""
        length = 0

        while True:

            for header in request.header_data:

                if isinstance(header, headers.Name):
                    name = header.decode()
                    print("Receiving %s" % name)
                elif isinstance(header, headers.Length):
                    length = header.decode()
                    print("Length %i" % length)
                elif isinstance(header, headers.Body):
                    body += header.decode()
                    sys.stdout.write("\rReceived %i/%i bytes" % (len(body),
                                                                 length))
                elif isinstance(header, headers.EndOfBody):
                    body += header.decode()
                    print(" (finished)")

            if request.is_final():
                break

            # Ask for more data.
            self.send_response(socket, responses.Continue())

            # Get the next part of the data.
            request = self.request_handler.decode(socket)

        self.send_response(socket, responses.Success())

        name = os.path.split(name)[1]
        path = os.path.join(self.directory, name)
        print("Writing %s" % repr(path))

        open(path, "wb").write(body)


def run_server(device_address, port, directory):

    # Run the server in a function so that, if the server causes an exception
    # to be raised, the server instance will be deleted properly, giving us a
    # chance to create a new one and start the service again without getting
    # errors about the address still being in use.
    push_server = PushServer(device_address, directory)
    socket = push_server.start_service(port)
    try:
        push_server.serve(socket)
    except IOError:
        push_server.stop_service(socket)


def main():

    if len(sys.argv) != 4:

        sys.stderr.write(
            "Usage: %s <device address> <port> <directory>\n" % sys.argv[0])
        sys.exit(1)

    device_address = sys.argv[1]
    port = int(sys.argv[2])
    directory = sys.argv[3]

    if not os.path.exists(directory):
        os.mkdir(directory)

    while True:
        run_server(device_address, port, directory)


if __name__ == "__main__":

    main()
