from . import headingreducer
from . import histogram

from .abstractparser import AbstractParser


class Parser(AbstractParser):
    def match(self, line):
        """test line whether matches with re header
        line is strippd string
        if matches, this function returns a not None objece, which might be passed to
        parse function
        """
        if line == 'Distribution Function: Slowing Down Time':
            return True
        return None

    def parse(self, einput, mboj=None):
        """
        called when reheader matches.
        Load several following lines, parse and reteurn as a object
        einput is like enumerate(stream)
        mobj is an object generated from match()
        """
        return histogram.parse(einput)


if __name__ == '__main__':
    import sys
    import argparse

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input', type=argparse.FileType('rt'),
                           default=sys.stdin, nargs='?', help='input file')
    argparser.add_argument('output', type=argparse.FileType('wt'),
                           default=sys.stdout, nargs='?', help='output file')

    args = argparser.parse_args()

    parser = Parser()
    h = headingreducer.HeadingReducer(args.input)
    for lineno, line in h:
        m = parser.match(line.strip())
        if m is not None:
            print('matched at line', lineno, file=sys.stderr)
            m = parser.parse(h, m)
            for c, v in zip(m.channel, m.data):
                print(c, v, file=args.output)
