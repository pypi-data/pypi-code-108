"""
parse "Detailed Description of the Cascade, Part 2 of 3" section

output routine is found at cascade/report.mfs:3340
"""

from .abstractparser import testframe
from .fixedfieldparser import FixedFieldParser
from .cascade_report_largetable import Parser as CascParser


class Parser(CascParser):
    # section title to match
    strippedtitle = 'Detailed Description of the Cascade, Part 2 of 3'
    title = ' '*42 + strippedtitle + '\n'

    # recordheader
    recordheader = ' '*6 + ' '*9 + 'File   Atom    KARMA' + \
        ' '*6 + 'Final Time' + ' '*7 + 'Final Energy' + ' '*12 + \
        '...Final Direction Cosines....' + '\n'

    # tuple of variablename and position to be stripped
    # field struct is (6X,I13,4X,A2,I9,3G18.6,2G15.6)
    recordparser = FixedFieldParser(
        [(None, 6, None),
         ('File', 13, int),
         (None, 4, None),
         ('Atom', 2, lambda a:a.strip()),
         ('Karma', 9, int),
         ('Final Time', 18, float),
         ('Final Energy', 18, float),
         ('Final Direction Cosine X', 18, float),
         ('Final Direction Cosine Y', 15, float),
         ('Final Direction Cosine Z', 15, float)])


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
