"""
abstract class for parser
"""

import sys
import json

from . import headingreducer


class ParseErrorException(Exception):
    """Exceptions when parsing error occurs

    args[0] consists of following dict key:values
        args[0]['lineno'] is line number where this exception is raised.
        args[0]['line'] is the line contents where this execption is raised.
        args[0]['mobj'] is parsed object just before exception occurs
    """
    pass


class AbstractParser(object):
    def match(self, line, **kw):
        """test whether string matches this parser.

        line is a stripped string to be tested.
        kw is optional dict argument

        returns non-None object if line matches, which will be passed to parse method
        """
        raise NotImplementedError

    def parse(self, einput, mobj=None, **kw):
        """read some lines from enumerated stream and parse.
        This will be explicitly called after match methods

        einput is enumareted text stream such as enumerate(sys.stdin).
        mobj is an object retuned from match().
        kw is optional dict argument

        returns parsed object

        this might raise ParseErrorException
        """
        raise NotImplementedError


# helper tools to parser fixed width format
# simple test framework
def testframe(parser, infile, outfile):
    """typical usage of parser object

    parser is Parser objcect
    input is input stream to be parsed
    output is output stream to show result
    """

    h = headingreducer.HeadingReducer(infile)

    for lineno, line in h:
        m = parser.match(line.strip())
        if m is not None:
            print('matched at line', lineno, file=sys.stderr)
            try:
                m = parser.parse(h, m)
            except ParseErrorException as e:
                args = e.args[0]
                print('parse exception at line', args['lineno'], '. this line is parsed again.', file=outfile)
                print('  line:', args['line'])
                print('  baseargs:', args['baseargs'])
                m = args['mobj']
                # hold this line again
                h.hold()

            json.dump(m, outfile, indent=2)
