"""
parse large table format output by cascade/report.mfs routines
  such as, "Detailed Description of the Cascade, Part ? of 3",
           "Lattice"
"""

from .abstractparser import AbstractParser
from .fixedfieldparser import FixedFieldParser


class Parser(AbstractParser):
    strippedtitle = ''
    title = ' '*42 + strippedtitle + '\n'

    recordheader = '\n'

    # tuple of variablename and position to be stripped
    recordparser = FixedFieldParser([])

    def match(self, strippedline):
        if strippedline == self.strippedtitle:
            return True
        return None

    def parse(self, einput, mobj, files=None):
        """Parse inputdata
        files is the number of record to be parsed. If files is None,
            parser stops at blank or illegal formatted line.
        """
        mobj = {'records': []}

        # skip one blank line
        next(einput)
        # get recordheader string
        lineno, line = next(einput)
        assert(line == self.recordheader)

        # contents
        filecount = 0
        while True:
            lineno, line = next(einput)
            # if line is blank, abort parseing
            strippedline = line.strip()
            if not strippedline:
                break
            # it might be a title and column header (if page is turned)
            if strippedline == self.strippedtitle:
                # one blankline
                lineno, line = next(einput)
                # one recordheaderline
                lineno, line = next(einput)
                assert(line == self.recordheader)
                # recordline
                lineno, line = next(einput)

            try:
                mobj['records'].append(self.recordparser.parse(line))
                filecount += 1
                if files and filecount >= files:
                    break
            except:
                # Most in case that next section starts from the top of the page,
                # hold this line and finish this parser
                # raise ParseErrorException({
                #     'lineno':lineno,
                #     'line':line,
                #     'mobj':mobj,
                #     'baseargs':e.args})
                einput.hold()
                break

        return mobj
