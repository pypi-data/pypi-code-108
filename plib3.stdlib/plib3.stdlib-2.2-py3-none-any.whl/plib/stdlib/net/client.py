#!/usr/bin/env python3
"""
MODULE CLIENT - Socket Client Objects
Sub-Package STDLIB.NET of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import errno
import socket


class SimpleClient(object):
    
    bufsize = 4096
    
    def __init__(self, transport, auto_run=True):
        self.transport = transport
        self.auto_run = auto_run
        
        self.sock = None
        self.connect_addr = None
        self.actual_addr = None
        self.connect_pending = False
        self.connected = False
        self.send_data = b""
        self.recv_data = b""
        self.comm_started = False
        self.closed = False
    
    # Low-level methods, should not need to be called by user
    
    def _sock_op(self, default, fn, *args,
                 default_errors=(errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN, errno.ECONNABORTED)):
        try:
            return fn(*args)
        except socket.error as e:
            self.close()
            if e.errno in default_errors:
                return default
            self.on_error(e)
            return
    
    def send(self, data):
        return self._sock_op(0, self.sock.send, data)
    
    def recv(self, buffer_size):
        return self._sock_op(b"", self.sock.recv, buffer_size)
    
    def handle_connect(self):
        self.connected = True
        self.on_connect()
    
    def readable(self):
        return not (self.closed or (self.connected and self.send_data))
    
    def writable(self):
        return (not self.closed) and ((not self.connected) or bool(self.send_data))
    
    def handle_read(self,
                    peek_flag=socket.MSG_PEEK):
        
        if self.connect_pending:
            # A nonblocking connect might signal connection refused with a read event
            self.connect_pending = False
            if not self.sock:
                return
            try:
                self.sock.recv(1, peek_flag)
            except socket.error as e:
                try:
                    self.close()
                except socket.error:
                    pass
                self.on_error(e)
                return
        data = self.recv(self.bufsize)
        if data:
            self.recv_data += data
        if self.check_message_complete(data):
            data = self.recv_data
            self.recv_data = b""
            self.on_receive(data)
    
    def handle_write(self):
        if self.connect_pending:
            # A nonblocking connect might signal completion or connect error with the first write event
            self.connect_pending = False
            if not self.sock:
                return
            try:
                self.actual_addr = self.sock.getpeername()
            except socket.error as e:
                try:
                    self.close()
                except socket.error:
                    pass
                self.on_error(e)
                return
            else:
                self.handle_connect()
        if self.send_data:
            sent = self.send(self.send_data)
            self.send_data = self.send_data[sent:]
    
    def close(self,
              closed_errors=(errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN, errno.ECONNABORTED, errno.EBADF)):
        
        if not self.closed:
            self.connected = False
            try:
                self.sock.close()
            except socket.error as e:
                if e.errno in closed_errors:
                    pass
                else:
                    self.on_error(e)
                    return
            self.sock = None
            self.actual_addr = None
            self.closed = True
            self.on_close()
    
    # "Manual" API methods, normally not needed since the public API or transport will call them as necessary
    
    def start_comm(self):
        if not self.comm_started:
            self.comm_started = True
            self.transport.add_handler(
                self.sock,
                self.readable,
                self.handle_read,
                self.writable,
                self.handle_write,
                self.check_done,
                self.end_comm
            )
            if self.auto_run:
                self.transport.run()
    
    def end_comm(self):
        self.close()
        self.comm_started = False
    
    # Public API methods
    
    def do_connect(self, addr,
                   connected_errors=(0, errno.EISCONN),
                   pending_errors=(errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK)):
        
        self.connect_addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.transport.nonblocking:
            self.sock.setblocking(0)
        err = self.sock.connect_ex(addr)
        if err in connected_errors:
            self.handle_connect()
        elif err in pending_errors:
            self.connect_pending = True
        else:
            self.on_error(socket.error(err, errno.errorcode[err]))
            return
        if self.transport.nonblocking and not self.connected:
            # So the nonblocking connect can complete
            self.start_comm()
    
    def send_message(self, data):
        # Note that this doesn't actually send anything, it just queues data;
        # it is assumed that an event loop will trigger the send
        if self.send_data:
            raise RuntimeError("Simple Client cannot send more than one message at a time.")
        self.send_data = data
        self.start_comm()
    
    # Methods that may need to be overridden, but do not have to be
    
    def on_error(self, e):
        raise e
    
    def check_message_complete(self, data):
        # Default is that any non-empty data is a valid message;
        # called in handle_read above to determine when to call on_receive
        return bool(data)
    
    def check_done(self):
        # Default is to only be done if the socket is closed (this ensures
        # proper behavior on an error); this will almost always need to be
        # overridden; called by the transport after each read/write event
        # is handled
        return self.closed
    
    # Methods to be overridden in subclasses
    
    def on_connect(self):
        # Called as soon as connect is known to be successful
        pass
    
    def on_receive(self, data):
        # Called when a complete message is received, data is the message
        pass
    
    def on_close(self):
        # Called when done and the socket has been closed
        pass
