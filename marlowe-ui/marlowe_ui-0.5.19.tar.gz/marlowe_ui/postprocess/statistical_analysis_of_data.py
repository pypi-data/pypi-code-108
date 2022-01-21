"""
'Statistical Analysis of Data for Si Atoms in \d+ Cascades'

output routine is found at final/slavex.mfs:2050
  enabled when INOFORM(3) == True
"""

import re

from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser

import logging

logger = logging.getLogger(__name__)

class AssertionError(Exception):
    """Exception object raised when assertion is failed
    args[0]: failed keyname
    """
    pass

# for output as csv format
csvheaders = ['Total number of', 'Mean', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev', 'Error']
csvcolumnkeys = csvheaders[1:]
csvrowheaders = ['Collisions', 'Atoms available for pairing', 'Sites available for pairing',
                 'Pairs identified', 'Pair separations > VCR', 'Unpaired vacant sites',
                 'Atoms escaping all surfaces', 'Replacement sequences',
                 'Focuson sequences', 'Truncated trajectories']

class Parser(AbstractParser):
    # 6X,35X,'Statistical Analysis of Data from',I8,' Cascades'
    title = re.compile(r'Statistical Analysis of Data from\s*(?P<samples>\d+) Cascades')

    # columnheader
    # Character*30 KNAME(19)
    #  DATA KNAME/'  .....Total number of.....','Collisions',		TTLS1460
    # 1	'Atoms available for pairing','Sites available for pairing',	TTLS1470
    # 2	'Pairs identified','Pair separations > VCR',			TTLS1480
    # 3	'Unpaired vacant sites','Atoms escaping all surfaces',		TTLS1490
    # 4	'Atoms trapped at all surfaces','Replacement sequences',	TTLS1500
    # 5	'Focuson sequences','Truncated trajectories',			TTLS1510
    # 6	'Beheaded replacement sequences','Beheaded focuson sequences',	TTLS1520
    # 7	'Redisplaced sequence members','Other redisplaced targets',	TTLS1530
    # 8	'Redisplacements, distant pairs','Redisplaced adatoms', 	TTLS1540
    # 9	'Multiple redisplacements'/					TTLS1550
    # Character*8 MOMX(6)
    #  DATA MOMX/'  Mean  ', 'Variance', 'Skewness', 'Kurtosis', 	TTLS0120
    # 1		'Std Dev ', ' Error  '/ 				                TTLS0130
    # (6X,A,4X,A,5(7X,A)/) KNAME(1), MOMX
    momx = ['  Mean  ', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev ', ' Error  ']
    columnheader = \
        ' '*6 + '{0:30s}'.format('  .....Total number of.....') +\
        ' '*4 + (' '*7).join(['{0:8s}'.format(i) for i in momx]) + '\n'

    # tuple of variablename and position to be stripped
    # field struct is (6X,A30,6G15.6)
    recordparser = FixedFieldParser(
        [(None, 6, None),
         ('Name', 30, str),
         ('Mean', 15, float),
         ('Variance', 15, float),
         ('Skewness', 15, float),
         ('Kurtosis', 15, float),
         ('Std Dev', 15, float),
         ('Error', 15, float)])

    def match(self, line):
        m = self.title.match(line)
        if m:
            mobj = {
                'strippedtitle': line,
                'samples': int(m.group('samples'))}
            return mobj
        return None

    def parse(self, einput, mobj):
        # skip one blank line
        next(einput)
        # get header string
        lineno, line = next(einput)
        assert(line == self.columnheader)
        # skip one blank line
        lineno, line = next(einput)

        # contents
        while True:
            lineno, line = next(einput)
            # if line is blank, abort parseing
            strippedline = line.strip()
            if not strippedline:
                break
            # it might be a title and column header (if page is updated)
            if strippedline == mobj['strippedtitle']:
                # one blankline
                lineno, line = next(einput)
                # one columnheaderline
                lineno, line = next(einput)
                # one blankline
                lineno, line = next(einput)
                # recordline
                lineno, line = next(einput)

            try:
                obj = self.recordparser.parse(line)
            except Exception as e:
                logger.info('error at fixedFieldParser ' + str(e))
                einput.hold()
                return mobj
            try:
                key = obj['Name'].strip()
                if key not in csvrowheaders:
                    raise AssertionError(key)
                del(obj['Name'])
                mobj[key] = obj
            except AssertionError:
                logger.info('AssersionError' + str(e))
                einput.hold()
                return mobj
            
        return mobj


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
