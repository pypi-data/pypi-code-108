
"""Collections of distinct ip-addresses.
"""

import struct
import base64
import ipaddr
import codecs


class IPList(object):
    """List (well, actually more of a set) of ip-addresses (well, actually
       using subnets...).
    """

    def __init__(self, iterable=()):
        self._addys = set()
        for ipaddy in iterable:
            self.add(ipaddy)

    def add(self, ipaddy):
        "Add ipaddy to self."
        if isinstance(ipaddy, str):
            ipaddy = ipaddr.IPv4Address(ipaddy)
        self._addys.add(ipaddy)

    def network(self):
        "Return the list of networks that cover our list of ip-addys."
        return ipaddr.collapse_address_list(self._addys)

    def __iter__(self):
        "Iterate over all network addresses in self."
        for ipaddy in sorted(self._addys):
            yield ipaddy

    def __eq__(self, other):
        # pylint:disable=W0212
        return len(self._addys ^ other._addys) == 0

    def pack(self):
        """Convert to compressed, but db friendly, notation.
           This fits ~124 ip addys into 250 bytes, if they are sufficiently
           contigous.
        """
        pstr = b''.join([a.packed for a in self])
        pzip = codecs.encode(pstr, 'zip')
        b64val = base64.urlsafe_b64encode(pzip)
        return b64val.decode('ascii')

    def unpack(self, b64val):
        "Reverse steps in pack()."
        pzip = base64.urlsafe_b64decode(b64val.encode('ascii'))
        pstr = codecs.decode(pzip, 'zip')

        while pstr:
            val, pstr = pstr[:4], pstr[4:]
            self.add(ipaddr.IPv4Address(struct.unpack("!I", val)[0]))

    __getstate__ = pack
    __setstate__ = unpack

    def __json__(self):
        return [a.compressed for a in self]

    def __repr__(self):
        return 'IPList(%r)' % list(self)

    def __str__(self):
        return ', '.join([a.compressed for a in self])
