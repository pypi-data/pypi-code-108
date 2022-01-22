#!/usr/bin/env python3
"""
Module TRANSPORT - Socket Transport Objects
Sub-Package STDLIB.NET of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import selectors


class SelectHandler(object):
    
    def __init__(self, loop, sock, readable, handle_read, writable, handle_write, done, end):
        self.loop = loop
        self.sock = sock
        self.readable = readable
        self.handle_read = handle_read
        self.writable = writable
        self.handle_write = handle_write
        self.done = done
        self.end = end
    
    def handle_event(self, mask,
                     read_event=selectors.EVENT_READ, write_event=selectors.EVENT_WRITE):
        
        if self.readable() and (mask & read_event):
            self.handle_read()
        if self.writable() and (mask & write_event):
            self.handle_write()
        if self.done():
            self.loop.remove_handler(self.sock)
            self.end()


class SelectLoop(object):
    
    nonblocking = True
    
    def __init__(self):
        self.handlers = {}
        self._sel = None
        self.running = False
    
    @property
    def sel(self):
        if not self._sel:
            self._sel = selectors.DefaultSelector()
        return self._sel
    
    def close(self):
        if self._sel:
            self._sel.close()
            self._sel = None
    
    def add_handler(self, sock, readable, handle_read, writable, handle_write, done, end):
        handler = SelectHandler(self, sock, readable, handle_read, writable, handle_write, done, end)
        self.handlers[sock] = handler
        self.sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, handler.handle_event)
    
    def remove_handler(self, sock):
        self.sel.unregister(sock)
        del self.handlers[sock]
    
    def run(self):
        if not self.running:
            self.running = True
            handlers = self.handlers
            select = self.sel.select
            close = self.close
            try:
                while handlers:
                    events = select()
                    for key, mask in events:
                        key.data(mask)
            finally:
                close()
                self.running = False
