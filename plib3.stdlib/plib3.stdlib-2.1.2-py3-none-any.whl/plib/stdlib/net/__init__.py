#!/usr/bin/env python3
"""
Sub-Package STDLIB.NET of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains useful utilities for network
detection and communication. It contains network client and
transport classes, and utility functions. Currently the
only utility function implemented is ``found_network``, which
takes an IP address prefix (e.g, 192.168.1) and determines
whether any network interface on the machine has an address
with that prefix.
"""

import sys

from plib.stdlib.builtins import first

if sys.platform == 'darwin':
    # OS X makes it hard to parse ifconfig, but we have no choice
    # (the IOCTL stuff we use on Linux isn't there, and we can't
    # rely on socket.gethostname to give us a real IP address either)
    
    from plib.sdtlib.proc import process_output
    
    
    def _entries(s):
        entry = []
        entry_started = False
        for line in s.splitlines():
            if (not entry) or line.startswith('\t'):
                entry.append(line)
            else:
                yield entry
                entry = [line]
    
    
    def _entry_has_network(entry, netprefix):
        return first(line for line in entry if netprefix in line)
    
    
    def found_network(netprefix):
        s = process_output('/sbin/ifconfig')
        if s:
            s = s.strip()
            for entry in _entries(s):
                line = _entry_has_network(entry, netprefix)
                if line:
                    loc = line.find(netprefix)
                    end = line.find(' ', loc)  # space ends the IP address
                    return line[loc:end]
        return None


elif sys.platform.startswith('linux'):
    
    import socket
    import fcntl
    import struct
    import array
    
    
    ENTRY_LEN = 40
    
    
    def _buf_name(buf):
        return buf.split(b'\0', 1)[0].decode('ascii')
    
    
    def _interface_str(entrylen=ENTRY_LEN):
        # This is faster and less prone to breakage than parsing ifconfig
        max_possible = 16  # arbitrary, raise if needed
        maxbytes = max_possible * entrylen
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', b'\0' * maxbytes)
        outbytes = struct.unpack(
            'iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', maxbytes, names.buffer_info()[0]))
        )[0]
        namestr = names.tostring()
        return outbytes, namestr
    
    
    def _all_interfaces(entrylen=ENTRY_LEN):
        outbytes, namestr = _interface_str(entrylen)
        return ((_buf_name(namestr[i:i + 16]), socket.inet_ntoa(namestr[i + 20:i + 24]))
                for i in range(0, outbytes, entrylen))
    
    
    def found_network(netprefix):
        return first(ifaddr
                     for _, ifaddr in _all_interfaces()
                     if ifaddr.startswith(netprefix))


else:  # Win32 and FreeBSD -- strange bedfellows :-)
    
    import socket
    
    
    def found_network(netprefix):
        # It would be nice if we could always use this simple method, but
        # it doesn't appear to work consistently on Linux or OS X (only
        # localhost appears)
        return first(ipaddr
                     for ipaddr in socket.gethostbyname_ex(socket.gethostname())[2]
                     if ipaddr.startswith(netprefix))
