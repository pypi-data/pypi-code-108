'''reduce header and blank line'''

class LineReducer():
    '''skip page header lines and blank line
    it yields, lineno, line as silimer to enumerate(file).

    This class has hold() method, if self.held is True,
    same lineno and line is yielded at following next() method.
    '''

    # peage header string
    # see general/global.mfs: GLBL0440
    #     general/liner.mfs: LINR0510
    headerstring = '''MARLOWE (Version 15b)   System:'''

    def __init__(self, input_, return_stripped=False):
        self.input = enumerate(input_)
        self.pagecount = 1  # page count starts from 1
        self.held = False
        self.lineno = -1
        self.line = None
        self.strippedline = None
        self.return_stripped = return_stripped

    def __iter__(self):
        return self

    def __next__(self):
        # read one line
        if self.held:
            self.held = False
            if self.return_stripped:
                return self.lineno, self.strippedline
            else:
                return self.lineno, self.line
        else:
            while self.input:
                # read next line
                self.lineno, self.line = next(self.input)

                if self.line.startswith('\x0c'):
                    self.pagecount += 1

                self.strippedline = self.line.strip()

                if len(self.strippedline) == 0 or \
                        self.strippedline.startswith(self.headerstring):
                    # skip
                    continue
                if self.return_stripped:
                    return self.lineno, self.strippedline
                else:
                    return self.lineno, self.line
            raise StopIteration

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

    for lineno, line in LineReducer(args.input):
        args.output.write('{0:d}'.format(lineno) + ':' + line)
