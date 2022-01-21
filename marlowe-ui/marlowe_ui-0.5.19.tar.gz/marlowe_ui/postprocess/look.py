"""Parse 'look' section in MRLN3740
"""

import re

from . import headingreducer

reheader = re.compile(
    '((No individual cascade output was requested)|'
    '(A description of the individual cascades was requested: LOOK =  (?P<look>\d)))')


class Parser(object):
    @staticmethod
    def match(line):
        """test line whether matches with re header
        line is strippd string
        if matches, this function returns a not None objece, which might be passed to
        parse function
        """
        m = reheader.match(line)
        if m:
            if m.group('look'):
                return int(m.group('look'))
            else:
                return 0
        return None

    @staticmethod
    def parse(einput, mobj=None):
        return mobj

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=argparse.FileType('rt'),
                        default=sys.stdin, nargs='?', help='input file')
    parser.add_argument('output', type=argparse.FileType('wt'),
                        default=sys.stdout, nargs='?', help='output file')

    args = parser.parse_args()

    h = headingreducer.HeadingReducer(args.input)

    for lineno, line in h:
        m = Parser.match(line.strip())
        if m is not None:
            print('matched at line', lineno, file=sys.stderr)
            m = Parser.parse(h, m)
            print(m, file=args.output)
