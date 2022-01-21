"""eliminate pagebreak and pageheader
"""


class HeadingReducer(object):
    """skip page header lines,

    it yields, lineno, line as silimer to enumerate(file).

    This class has hold() method, if hold is called,
    same lineno and line is yielded at following next() method.
    """
    def __init__(self, input):
        self.input = enumerate(input)
        self.pagecount = 1  # page count starts from 1
        self.held = False
        self.lineno = -1
        self.line = None

    def __iter__(self):
        return self

    def __next__(self):
        # read one line
        if self.held:
            self.held = False
        else:
            self.lineno, self.line = next(self.input)

            if self.line and self.line[0] == '\x0c':
                self.pagecount += 1
                if self.pagecount % 2 == 0:
                    # odd->even page
                    # skip 1 line
                    next(self.input)
                else:
                    # even->odd page
                    # skip 5 lines
                    for i in range(5):
                        next(self.input)
                self.lineno, self.line = next(self.input)
        return self.lineno, self.line

    def hold(self):
        self.held = True


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=argparse.FileType('rt'),
                        default=sys.stdin, nargs='?', help='input file')
    parser.add_argument('output', type=argparse.FileType('wt'),
                        default=sys.stdout, nargs='?', help='output file')

    args = parser.parse_args()

    for lineno, line in HeadingReducer(args.input):
        args.output.write('{0:d}'.format(lineno) + ':' + line)
