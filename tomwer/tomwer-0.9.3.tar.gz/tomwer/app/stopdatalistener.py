#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from tomwer.core.process.control.datalistener.rpcserver import (
    send_signal_to_local_rpc_servers,
)
from tomwer.core.settings import JSON_RPC_PORT
from signal import SIGTERM, SIGKILL


def getinputinfo():
    return "tomwer stop-data-listener [[--port --sigkill]]"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port",
        default=JSON_RPC_PORT,
        help="Define the port occupy by the rpc-server",
    )
    parser.add_argument(
        "--sigkill",
        action="store_true",
        default=False,
        help="send a SIGKILL signal instead of a SIGTERM",
    )
    options = parser.parse_args(argv[1:])
    signal = SIGTERM
    if options.sigkill:
        signal = SIGKILL
    send_signal_to_local_rpc_servers(port=int(options.port), signal=signal)


if __name__ == "__main__":
    main(sys.argv)
