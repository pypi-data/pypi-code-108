#!/usr/bin/env python3
"""
PYGET.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple clone of the wget program that can fetch multiple
files in one invocation. Only speaks HTTP 1.0 and does not
do SSL or any port other than 80.
"""

import os
import socket
from urllib.parse import urlparse

from plib.stdlib.builtins import first

from plib.stdlib.net.client import SimpleClient
from plib.stdlib.net.transport import SelectLoop


# Use HTTP 1.0 to avoid having to support any fancy stuff

request_tmpl = "GET {} HTTP/1.0\r\nHost: {}\r\n\r\n"


class WGetClient(SimpleClient):
    
    def __init__(self, transport, url, auto_run=True):
        SimpleClient.__init__(self, transport, auto_run=auto_run)
        self.done = False
        
        print("initializing client for url:", url)
        parts = urlparse(url)
        self.host = parts.netloc
        self.path = parts.path
        self.filename = parts.path.split("/")[-1]
        
        addr = (socket.gethostbyname(parts.netloc), 80)
        print("connecting to", addr)
        self.do_connect(addr)
    
    def on_error(self, e):
        print("Socket error: {}".format(str(e)))
    
    def on_connect(self):
        print("connected to", self.actual_addr)
        data = request_tmpl.format(self.path, self.host)
        print("Sending request:")
        print(data)
        self.send_message(data.encode())
    
    def check_message_complete(self, data):
        # The only completion check we need is a closed socket on the other end
        return not data
    
    def get_content_length(self, headers,
                           prefix="Content-Length: "):
        
        lines = headers.splitlines()
        line = first(s for s in lines if s.startswith(prefix))
        return int(line[len(prefix):]) if line else None
    
    def on_receive(self, data):
        headers, data = data.split(b"\r\n\r\n", 1)
        headers = headers.decode()
        print("received headers:")
        print(headers)
        print()
        content_length = self.get_content_length(headers)
        if content_length is None:
            print("possible data error: unable to parse content length from headers")
        elif content_length != len(data):
            print("possible data corruption: expected {} data bytes but received {}")
        print("saving data to", self.filename)
        with open(self.filename, 'wb') as f:
            f.write(data)
        self.done = True
    
    def check_done(self):
        return self.done or super(WGetClient, self).check_done()


def run_wget(urls, auto_run):
    transport = SelectLoop()
    clients = [WGetClient(transport, url, auto_run=auto_run) for url in urls]
    # Only need to run transport manually if auto_run is False; however, if auto_run
    # is true the clients will connect and send their requests sequentially instead of
    # in parallel
    if not auto_run:
        transport.run()


if __name__ == '__main__':
    import sys
    
    # The auto_run parameter determines whether or not each client automatically calls
    # the transport's run method when it starts; if it does, then the clients will end
    # up running sequentially instead of in parallel, and the output will show the difference
    auto_run = any(s in ('--auto_run', '-a') for s in sys.argv[1:])
    
    urls = [s for s in sys.argv[1:] if not s.startswith('-')]
    run_wget(urls, auto_run)
