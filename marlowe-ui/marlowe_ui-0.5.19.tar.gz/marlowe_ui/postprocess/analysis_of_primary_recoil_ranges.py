"""
'Analysis of Primary Recoil Ranges (   \d+ Stopped Particles)' section
shown at final/rangex.mfs:
"""

import re

from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser


class Parser(AbstractParser):
    # '(6X,30X,A,I6,A//6X,17X,6(8X,A)/(6X,3X,A,6G16.6))' )	RNGX0830
    reheader = re.compile(r'Analysis of Primary Recoil Ranges \(\s*(?P<Samples>\d+) Stopped Particles\)')

    def match(self, line, env=None):
        m = self.reheader.match(line)
        if m:
            return {'Samples': int(m.group('Samples'))}
        return None

    # tuple of variablename and position to be stripped
    # field struct is 6X,3X,A18,6G16.6
    recordparser = FixedFieldParser(
        [(None, 6, None),
         (None, 3, None),
         (None, 18, None),
         ('Mean', 16, float),
         ('Variance', 16, float),
         ('Skewness', 16, float),
         ('Kurtosis', 16, float),
         ('Std Dev', 16, float),
         ('Error', 16, float)])

    def parse(self, einput, mobj, env=None):
        # skip one blank line
        next(einput)
        # get header string
        lineno, line = next(einput)

        # contents
        for key in ['Radial Range', 'Penetration', 'Spread', 'Total Path',
                    'Slowing Down Time']:
            lineno, line = next(einput)
            mobj[key] = self.recordparser.parse(line)
        # optional values, but not yet
        # ['Front Escape Time', 'Back Escape Time', 'Side Escape Time', 'Other Escape Time ']
        return mobj

# for output as csv format
csvheaders = ['Range of', 'Mean', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev', 'Error']
csvcolumnkeys = csvheaders[1:]
csvrowheaders = ['Radial Range', 'Penetration', 'Spread', 'Total Path', 'Slowing Down Time',
                 'Front Escape Time']

if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
