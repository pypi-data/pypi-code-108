#!/usr/bin/env python3

import sys

from PyOBEX import client, responses

if __name__ == "__main__":

    if len(sys.argv) != 4:

        sys.stderr.write(
            "Usage: %s <device address> <port> <file name>\n" % sys.argv[0])
        sys.exit(1)

    device_address = sys.argv[1]
    port = int(sys.argv[2])
    file_name = sys.argv[3]

    c = client.Client(device_address, port)
    # Note that the OBEXObjectPush UUID is not supplied as a Target header.
    # See version 1.1 of the Object Push Profile specification.
    r = c.connect()

    if not isinstance(r, responses.ConnectSuccess):
        sys.stderr.write("Failed to connect.\n")
        sys.exit(1)

    c.put(file_name, open(file_name, "rb").read())
    c.disconnect()

    sys.exit()
