"""
parse "Locations of the Cascade Latice Sites" section

output routine is found at cascade/report.mfs:3830
"""

from .abstractparser import testframe
from .fixedfieldparser import FixedFieldParser
from .cascade_report_largetable import Parser as CascParser


class Parser(CascParser):
    strippedtitle = 'Locations of the Cascade Lattice Sites'
    title = ' '*48 + strippedtitle + '\n'

    # recordheader
    recordheader = ' '*29 + 'File    Site' + ' '*12 +\
                   '...........Location...........' + ' '*10 + 'Paired Atom' + '\n'

    # tuple of variablename and position to be stripped
    # field struct is (6X,A30,6G15.6)
    recordparser = FixedFieldParser(
        [(None, 6, None), ('File', 27, int), ('Site', 7, int), (None, 4, None),
         ('Location X', 15, float), ('Location Y', 15, float),
         ('Location Z', 15, float), ('Paired Atom File', 12, int)])


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
