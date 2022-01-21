"""
parse "Detailed Description of the Cascade, Part 3 of 3" section

output routine is found at cascade/report.mfs:3530
"""

from .abstractparser import testframe
from .fixedfieldparser import FixedFieldParser
from .cascade_report_largetable import Parser as CascParser


class Parser(CascParser):
    # section title to match
    strippedtitle = 'Detailed Description of the Cascade, Part 3 of 3'
    title = ' '*42 + strippedtitle + '\n'

    # recordheader
    # original in the source
    recordheader_orig = ' '*6 + ' File   Atom\t  KARMA' + \
        ' '*11 + '........Final Location........' + \
        ' '*15 + '....Reference Lattice Site....' + ' '*8 + 'Site' + '\n'
    # in output .lst file tab character seems to be expanded
    recordheader = ' '*6 + ' File   Atom    KARMA' + \
        ' '*11 + '........Final Location........' + \
        ' '*15 + '....Reference Lattice Site....' + ' '*8 + 'Site' + '\n'

    # tuple of variablename and position to be stripped
    # field struct is (6X,I5,4X,A2,I9,3X,6G15.6,I5)
    recordparser = FixedFieldParser(
        [(None, 6, None),
         ('File', 5, int),
         (None, 4, None),
         ('Atom', 2, lambda a:a.strip()),
         ('Karma', 9, int),
         (None, 3, None),
         ('Final Location X', 15, float),
         ('Final Location Y', 15, float),
         ('Final Location Z', 15, float),
         ('Reference Lattice Site X', 15, float),
         ('Reference Lattice Site Y', 15, float),
         ('Reference Lattice Site Z', 15, float),
         ('Reference Lattice Site', 6, int)])


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
