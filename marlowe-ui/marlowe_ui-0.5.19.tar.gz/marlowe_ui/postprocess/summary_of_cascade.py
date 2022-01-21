"""Parse '.....Total number of.....' section in cascade summary
shown at cascade/report:150
"""

import re

from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser


def _gen_field(fieldname):
    return [(None, 16, None), ('_'+fieldname, 30, str, '{0:30s}'.format(fieldname)),
            (fieldname, 10, int)]


class Parser(AbstractParser):

    # see cascade/report.mfs RPRT4810
    #  330 FORMAT(6X,31X,'Summary of Cascade',I6,':',5X,'Group',I5,5X,'NumberRPRT4790
    #     1',I3//6X,10X,A,26X,A//6X,10X,A,I10/(6X,10X,A,I10,16X,A,I10))	RPRT4800
    strippedtitle_re = re.compile(
        r'Summary of Cascade\s*(?P<Cascade>\d+):\s+'
        'Group\s*(?P<Group>\d+)\s+'
        'Number\s*(?P<Number>\d+)')

    # CHARACTER*30 KNAME(19)
    recordparsers = [
        FixedFieldParser(_gen_field('Collisions')),
        FixedFieldParser(_gen_field('Atoms available for pairing')
                         + _gen_field('Sites available for pairing')),
        FixedFieldParser(_gen_field('Pairs identified')
                         + _gen_field('Pair separations > VCR')),
        FixedFieldParser(_gen_field('Unpaired vacant sites')
                         + _gen_field('Atoms escaping all surfaces')),
        FixedFieldParser(_gen_field('Atoms trapped at all surfaces')
                         + _gen_field('Replacement sequences')),
        FixedFieldParser(_gen_field('Focuson sequences')
                         + _gen_field('Truncated trajectories')),
        FixedFieldParser(_gen_field('Beheaded replacement sequences')
                         + _gen_field('Beheaded focuson sequences')),
        FixedFieldParser(_gen_field('Redisplaced sequence members')
                         + _gen_field('Other redisplaced targets')),
        FixedFieldParser(_gen_field('Redisplacements, distant pairs')
                         + _gen_field('Redisplaced adatoms')),
        FixedFieldParser(_gen_field('Multiple redisplacements'))]

    def match(self, strippedline):
        m = self.strippedtitle_re.match(strippedline)
        if m:
            return {'Cascade': int(m.group('Cascade')),
                    'Group': int(m.group('Group')),
                    'Number': int(m.group('Number'))}
        return None

    def parse(self, einput, mobj):
        # skip one blank line
        next(einput)
        # skip one title line
        next(einput)
        # skip one blank line
        next(einput)

        for p, (lineno, line) in zip(self.recordparsers, einput):
            mobj.update(p.parse(line))

        return mobj

if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
