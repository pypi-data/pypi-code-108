"""parse histogram data

Title
(empty line)
(Histogram channel width [width]  Origin in Channel [origin]  First reported channel [first])
(empty line)
bin counts in multilines
(empty line)
"""

import re

from . import util


class Error(Exception):
    pass

reheader = re.compile(
    r'\(Histogram channel width\s+' + util.refloatstr('width') +
    r'\s+Origin in Channel\s+' + util.refloatstr('origin') +
    r'\s+First reported channel\s+' + util.refloatstr('first') + '\)')


class Histogram(object):
    def __init__(self, header, data):
        self.header = header
        self.width = float(self.header['width'])
        self.origin = int(self.header['origin'])
        self.first = int(self.header['first'])
        self.data = data
        self.channel = self._make_channel_data()

    def _make_channel_data(self):
        channel = []
        for i in range(len(self.data)):
            channel.append((i+self.origin+self.first)*self.width)

        return channel


def parse_header(line):
    m = reheader.match(line)

    if m is None:
        raise Error('cannot parse header line')

    return m.groupdict()


def parse(estream):
    """
    estream is like enumerate(stream)
    """
    # skip until non-blank line for header
    header = parse_header(util.skip_to_nonblankline(estream)[1])
    # skip to 1st data line
    lineno, line = util.skip_to_nonblankline(estream)
    # data line
    data = [float(s) for s in line.split()]
    for lineno, line in estream:
        line = line.strip()
        if line:
            data.extend([float(s) for s in line.split()])
        else:
            break

    return Histogram(header, data)
