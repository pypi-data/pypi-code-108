"""
Parse '(Elem), Primary Recoil Ranges' section
 in cascade/ranger.mfs:1160
"""

import re

from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser


class Parser(AbstractParser):
    # Si Primary Recoil Ranges
    strippedtitle_re = re.compile(r'(?P<Elem>\w+) Primary Recoil Ranges')

    # Radial  122.134       Penetration  121.445       Spread  12.9637       Total Path  129.751       Time (fs)  626.727   # noqa
    recordparser = FixedFieldParser([
        (None, 6, None),
        ('_Radial', len('Radial'), str, 'Radial'),
        ('Radial', 13, float),
        (None, 3, None),
        ('_Penetration', len('Penetration'), str, 'Penetration'),
        ('Penetration', 13, float),
        (None, 3, None),
        ('_Spread', len('Spread'), str, 'Spread'),
        ('Spread', 13, float),
        (None, 3, None),
        ('_Total Path', len('Total Path'), str, 'Total Path'),
        ('Total Path', 13, float),
        (None, 3, None),
        ('_Time (fs)', len('Time (fs)'), str, 'Time (fs)'),
        ('Time (fs)', 13, float)])

    def match(self, strippedline, env=None):
        m = self.strippedtitle_re.match(strippedline)
        if m:
            obj = {'Elem': m.group('Elem')}
            return obj
        else:
            return None

    def parse(self, einput, mobj, env=None):
        # skip one line
        next(einput)
        lineno, line = next(einput)
        m = self.recordparser.parse(line)
        if m:
            mobj['Radial Range'] = m['Radial']
            mobj['Penetration'] = m['Penetration']
            mobj['Spread'] = m['Spread']
            mobj['Total Path'] = m['Total Path']
            mobj['Slowing Down Time'] = m['Time (fs)']
        return mobj


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
