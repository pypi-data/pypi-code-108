#!/usr/bin/env python3
"""
Module SOCKET -- UI Socket Wrapper Objects
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import functools

from plib.ui.defs import *
from plib.ui.widgets import get_toolkit_class


class PSocketHandler(object):
    
    def __init__(self, transport, sock, readable, handle_read, writable, handle_write, done, end_notify):
        self.transport = transport
        self.sock = sock
        self.closed = False
        
        self.read_notifier = transport.notifier_class(sock, NOTIFY_READ, readable, self._wrap(handle_read, done, end_notify))
        self.write_notifier = transport.notifier_class(sock, NOTIFY_WRITE, writable, self._wrap(handle_write, done, end_notify))
    
    def close(self):
        if self.closed:
            return
        self.read_notifier.set_enabled(False)
        self.read_notifier = None  # no way to actually close the notifier, this is the best we can do
        self.write_notifier.set_enabled(False)
        self.write_notifier = None
        self.transport.remove_handler(self.sock)
        self.closed = True
    
    def _wrap(self, fn, done, end_notify):
        @functools.wraps(fn)
        def _f(sock):
            assert sock is self.sock
            fn()
            if done():
                self.close()
                end_notify()
        return _f


class PSocketTransport(object):
    
    notifier_class = get_toolkit_class('socket', 'PSocketNotifier')
    
    nonblocking = True  # for compatibility with plib.stdlib.net
    
    def __init__(self):
        self.handlers = {}
        self.started = False
    
    def add_handler(self, sock, readable, handle_read, writable, handle_write, done, end_notify):
        self.handlers[sock] = PSocketHandler(self, sock, readable, handle_read, writable, handle_write, done, end_notify)
    
    def run(self):
        # This tells the notifier to start processing socket events
        if self.handlers and not self.started:
            self.notifier_class.start()
            self.started = True
    
    def remove_handler(self, sock):
        del self.handlers[sock]
        if self.started and not self.handlers:
            # This tells the notifier to stop processing socket events
            self.notifier_class.done()
            self.started = False
