"""
parse "Detailed Description of the Cascade, Part 1 of 3" section

output routine is found at cascade/report.mfs:3080
"""

from .abstractparser import testframe
from .fixedfieldparser import FixedFieldParser
from .cascade_report_largetable import Parser as CascParser


class Parser(CascParser):
    strippedtitle = 'Detailed Description of the Cascade, Part 1 of 3'
    title = ' '*42 + strippedtitle + '\n'

    # recordheader
    recordheader = \
        '        File   Atom   KARMA   Initial Time   Initial Energy           ' \
        + '......Initial Location......          Site   TRAK   NSEQ\n'

    # tuple of variablename and position to be stripped
    # field struct is (6X,A30,6G15.6)
    recordparser = FixedFieldParser(
        [(None, 6, None),
         ('File', 6, int),
         (None, 4, float),
         ('Atom', 2, lambda a:a.strip()),
         ('Karma', 8, int),
         ('Initial Time', 16, float),
         ('Initial Energy', 16, float),
         ('Initial Location X', 16, float),
         ('Initial Location Y', 16, float),
         ('Initial Location Z', 16, float),
         ('Initial Location Site', 5, int),
         ('Trak', 8, int),
         ('Nseq', 6, int)])


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
