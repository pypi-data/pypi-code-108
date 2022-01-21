"""
parse 'Separations of Distant Interstitial-Vacancy Pairs' Section
in cascade/orgiv.mfs routine
"""

from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser


class Parser(AbstractParser):
    strippedtitle_valid = 'Separations of Distant Interstitial-Vacancy Pairs'
    title_valid = ' '*41 + strippedtitle_valid + '\n'

    strippedtitle_invalid = 'No distant vacancy-interstitial pairs found'
    title_invalid = ' '*44 + strippedtitle_invalid + '\n'

    # 6X,8X,'Pair',6X,'Vacancy     Interstitial    Separation',12X,
    # 'Pair',6X,'Vacancy	 Interstitial	 Separation'
    recordheader1 = \
        '              Pair      Vacancy     Interstitial    ' + \
        'Separation            Pair      Vacancy     Interstitial    Separation' + '\n'
    recordheader2 = \
        '             Number   Site   File   Atom    File     ' + \
        'Distance            Number   Site   File   Atom    File     Distance' + '\n'

    # tuple of variablename and position to be stripped
    recordparser_odd = FixedFieldParser([
        (None, 6, None),  # -6
        (None, 3, None),  # -9
        ('Pair Number', 8, int),   # -17
        ('Vacancy Site', 8, int),  # -25
        ('Vacancy File', 8, int),  # -33
        (None, 4, None),           # -37
        ('Interstitial Atom', 2, lambda a: a.strip()),  # -39
        ('Interstitial File', 9, int),  # -48
        ('Distance', 15, float)])  # -63
    odd_linewidth = 64  # 63 + len('\n')
    recordparser_even = FixedFieldParser([
        (None, 63, None),  # odd part
        (None, 6, None),
        ('Pair Number', 8, int),
        ('Vacancy Site', 8, int),
        ('Vacancy File', 8, int),
        (None, 4, None),
        ('Interstitial Atom', 2, lambda a: a.strip()),
        ('Interstitial File', 9, int),
        ('Distance', 15, float)])

    def __init__(self, pairs=None):
        """

        pairs is the number of record to be parsed. If pairs is None,
            parser stops at blank or illegal formatted line.
        """
        self.pairs = pairs

    def match(self, strippedline):
        if strippedline == self.strippedtitle_valid:
            return {'status': 'valid'}
        elif strippedline == self.strippedtitle_invalid:
            return {'status': 'invalid'}
        return None

    def parse(self, einput, mobj):
        """Parse inputdata

        einput is enumareted text stream such as enumerate(sys.stdin).
        mobj is an object retuned from match().
        """

        mobj['records'] = []

        if mobj['status'] == 'invalid':
            return mobj

        # skip one blank line
        next(einput)
        # get recordheader string
        lineno, line = next(einput)
        assert(line == self.recordheader1)
        lineno, line = next(einput)
        assert(line == self.recordheader2)

        paircount = 0
        # contents
        while True:
            lineno, line = next(einput)
            # if line is blank, abort parseing
            strippedline = line.strip()
            if not strippedline:
                break
            # it might be a title and column header (if page is updated)
            if strippedline == self.strippedtitle_valid:
                # one blankline
                lineno, line = next(einput)
                # one recordheaderline
                lineno, line = next(einput)
                assert(line == self.recordheader1)
                lineno, line = next(einput)
                assert(line == self.recordheader2)
                # recordline
                lineno, line = next(einput)

            try:
                # odd part
                mobj['records'].append(self.recordparser_odd.parse(line))
                paircount += 1
                # even part
                if len(line) > self.odd_linewidth:
                    mobj['records'].append(self.recordparser_even.parse(line))
                    paircount += 1
                if self.pairs and paircount >= self.pairs:
                    break
            except:
                # Most in case that next section starts from the top of the page,
                # hold this line and finish this parser
                # raise ParseErrorException({
                #     'lineno': lineno,
                #     'line': line,
                #     'mobj': mobj,
                #     'baseargs': e.args})
                einput.hold()
                break

        return mobj


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
