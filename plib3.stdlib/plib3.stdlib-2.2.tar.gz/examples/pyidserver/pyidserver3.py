#!/usr/bin/env python3
"""
PYIDSERVER.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of IDServer, a command-line tool
to query an internet server and return information
about it.
"""

import sys
import os
import collections
import socket

from plib.stdlib.net.client import SimpleClient
from plib.stdlib.net.transport import SelectLoop


def do_output(fileobj, s, linesep=True):
    fileobj.write(s)
    if linesep:
        fileobj.write(os.linesep)
    fileobj.flush()


PROTO_DEFAULT = 'http'

quitmsgs = [None, b"QUIT\r\n"]

protocols = {
    'ftp': (21, [None]),
    'http': (80, [b"HEAD / HTTP/1.0\r\n\r\n"]),
    'imap': (143, [None, b"A1 CAPABILITY\r\n", b"A2 LOGOUT\r\n"]),
    'news': (119, quitmsgs),
    'pop': (110, quitmsgs),
    'smtp': (25, quitmsgs)
}


class IDServerClient(SimpleClient):
    
    def __init__(self, transport, fileobj):
        self.done = False
        super(IDServerClient, self).__init__(transport)
        self.fileobj = fileobj
        self.items = collections.deque()
    
    def on_error(self, e):
        do_output(self.fileobj, "Socket error: {}".format(str(e)))
    
    def start(self):
        if self.items:
            next_item = self.items.popleft()
            self.send_message(next_item)
        else:
            self.done = True
    
    def on_connect(self):
        do_output(
            self.fileobj,
            "Connected ...{}Server returned the following:{}".format(os.linesep, os.linesep)
        )
        self.start()
    
    def check_message_complete(self, data):
        # This is not a good general way of detecting a complete message,
        # but it's good enough for this
        return (not data) or (len(data) < self.bufsize)
    
    def on_receive(self, data):
        do_output(self.fileobj, data.decode(), False)
        self.start()
    
    def check_done(self):
        return self.done  # no super call needed here since self.done is set to True on close
    
    def on_close(self):
        do_output(
            self.fileobj,
            "{}Connection closed.".format(os.linesep)
        )
        self.done = True  # this ensures the select loop exits even on an error
    
    def do_chat(self, addr, items):
        self.done = False
        self.items.extend(items)
        self.do_connect(addr)  # this will automatically start the transport
    
    def run(self, url, dns_only, protocol, portnum):
        if '://' in url:
            addrtype, url = url.split('://')
            if addrtype in protocols:
                if protocol:
                    do_output(
                        self.fileobj,
                        "URL includes protocol {}, ignoring specified protocol {}.".format(addrtype, protocol)
                    )
                protocol = addrtype
            elif addrtype:
                do_output(
                    self.fileobj,
                    "URL includes incorrect protocol {}, ignoring.".format(addrtype)
                )
        if '/' in url:
            url, path = url.split('/')
            if path:
                do_output(self.fileobj, "URL includes path, ignoring.")
        if ':' in url:
            url, portstr = url.split(':')
            try:
                p = int(portstr)
            except ValueError:
                do_output(
                    self.fileobj,
                    "URL includes invalid port {}, ignoring.".format(portstr)
                )
            else:
                if p != portnum:
                    if portnum != 0:
                        do_output(
                            self.fileobj,
                            "URL includes port {:d}, ignoring specified port {:d}.".format(p, portnum)
                        )
                    portnum = p
        
        if dns_only:
            do_output(self.fileobj, "Doing DNS lookup on {} ...".format(url))
        else:
            proto_msg = port_msg = ""
            if protocol == "":
                protocol = PROTO_DEFAULT
            else:
                protocol = protocol.lower()
                proto_msg = " using {}".format(protocol)
            if protocol in protocols:
                proto_port, proto_items = protocols[protocol]
                if portnum == 0:
                    portnum = proto_port
                else:
                    port_msg = " on port {:d}".format(portnum)
            else:
                raise ValueError("Invalid protocol: {}.".format(protocol))
        
        dns_failed = False
        try:
            ipaddr = socket.gethostbyname(url)
            if ipaddr == url:
                # URL was an IP address, reverse lookup
                try:
                    hostname = socket.gethostbyaddr(ipaddr)[0]
                except socket.herror:
                    hostname = "cannot be found"
                else:
                    hostname = "is {}".format(hostname)
                do_output(
                    self.fileobj,
                    "Domain name for {} {}.".format(ipaddr, hostname)
                )
            else:
                # URL was a domain name, normal lookup
                do_output(
                    self.fileobj,
                    "IP address for {} is {}.".format(url, ipaddr)
                )
        except (socket.herror, socket.gaierror) as e:
            dns_failed = True
            do_output(self.fileobj, "DNS lookup failed for {}.".format(url))
            do_output(self.fileobj, "Error info: {}".format(str(e)))
        
        if not (dns_only or dns_failed):
            do_output(self.fileobj, "Contacting {}{}{} ...".format(url, proto_msg, port_msg))
            self.do_chat((url, portnum), proto_items)


def run_main(url, outfile=sys.stdout, errfile=sys.stderr,
             dns_only=False, protocol="", portnum=0):
    """Query server and write results to a file-like object.
    
    This is the intended external API for pyidserver; it wraps the
    ``IDServerClient.run`` method, which does the work, with reasonable
    error handling and diagnostic output.
    
    The purpose of pyidserver is to query an internet server for
    basic information, and output it to the user. It does not actually
    "speak" any of the specific protocols for which it will query a
    server; it relies on the fact that most servers return some sort
    of informational "greeting" when a client connects to them, and
    the information it outputs is taken from such greetings.
    
    In the case of HTTP servers, a request must first be sent for the
    server to return any information (a HEAD request is used for this
    purpose). In the case of IMAP servers, an additional request after
    the first greeting (A1 CAPABILITY) is used to elicit additional
    information.
    
    In all cases where the session with the server is supposed to be
    explicitly terminated (all protocols supported except FTP),
    pyidserver does the termination when it is finished.
    
    Arguments:
    
    - ``url``: a URL string (either an IP address or a host name).
      May include a protocol specifier at the start (e.g., http://),
      and may include a port specifier at the end (e.g., :80). A
      trailing slash, '/', in the URL, and anything after it, are
      treated as a path specifier and ignored.
    
    - ``outfile``: the file-like object for output (actually it
      can be anything that has ``write`` and ``flush`` methods).
    
    - ``errfile``: a file-like object for error output (actually it
      can be anything with a ``write`` method).
    
    - ``dns_only``: If true, only a DNS lookup is done; no connection
      is actually made to the server.
    
    - ``protocol: one of the strings listed as keys in the
      ``protocols`` dictionary above (the default, if nothing is
      passed, is 'http').
    
    - ``portnum``: an integer giving the port number on the server.
      (This parameter should only need to be used very rarely;
      almost always the port number is determined by the protocol
      as shown in the dictionary above.)
    """
    
    try:
        client = IDServerClient(SelectLoop(), outfile)
        client.run(url, dns_only, protocol, portnum)
    except:
        exc_type, exc_value, _ = sys.exc_info()
        errfile.write("{} {}{}".format(str(exc_type), str(exc_value), os.linesep))


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    optlist = (
        ("-e", "--errfile", {
            'action': "store", 'type': str,
            'dest': "errfile", 'default': run_main.__defaults__[1],
            'help': "File-like object for error output"
        }),
        ("-f", "--outfile", {
            'action': "store", 'type': str,
            'dest': "outfile", 'default': run_main.__defaults__[0],
            'help': "File-like object for normal output"
        }),
        ("-l", "--lookup", {
            'action': "store_true",
            'dest': "dns_only", 'default': run_main.__defaults__[2],
            'help': "Only do DNS lookup, no server query"
        }),
        ("-p", "--protocol", {
            'action': "store", 'type': str,
            'dest': "protocol", 'default': run_main.__defaults__[3],
            'help': "Use the specified protocol to contact the server"
        }),
        ("-r", "--port", {
            'action': "store", 'type': int,
            'dest': "portnum", 'default': run_main.__defaults__[4],
            'help': "Use the specified port number to contact the server"
        })
    )
    arglist = ["url"]
    
    opts, args = parse_options(optlist, arglist)
    # Spot check the parsing results
    assert opts['dns_only'] == opts.dns_only
    assert args[0] == args.url
    
    run_main(args.url, opts.outfile, opts.errfile,
             opts.dns_only, opts.protocol, opts.portnum)
