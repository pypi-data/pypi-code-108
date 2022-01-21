from .abstractparser import AbstractParser
from . import util


class _ExamlpeParser(AbstractParser):
    def match(self, strippedline):
        # match with non-blank line
        if strippedline:
            return strippedline
        return None

    def parser(self, einput, mobj):
        # do nothing just return this line
        return mobj


class ParserChain(AbstractParser):
    def __init__(self):
        # chain of parsers [(section name, parser, postprocess, number of iterations)]
        self.parsers = []
        # index to parser and number of mulplicity
        self.parser_idx = 0
        self.parser_multiplicity = 0
        self.mobj = None

    def parse(self, einput):
        # clear internal paser state
        self.parser_idx = 0
        self.parser_multiplicity = 0
        while True:
            try:
                lineno, line = util.skip_to_nonblankline(einput)
            except StopIteration:
                break

            line = line.strip()

            # seek parsers to match
            for idx, (name, p, after, multiplicity) in enumerate(
                    self.parsers[self.parser_idx:], self.parser_idx):
                m = p.match(line)
                if m is not None:
                    # test multiplicity
                    if idx == self.parser_idx:
                        self.parser_multiplicity += 1
                    else:
                        self.parser_multiplicity = 1
                        self.parser_idx = idx

                    m = p.parse(einput, m)

                    if after:
                        after(m)
                    # next parser
                    if isinstance(multiplicity, int) and \
                            self.parser_multiplicity >= multiplicity:
                        # start at next parser
                        self.parser_idx = idx + 1
                        self.parser_multiplicity = 0
                    break
            if self.parser_idx >= len(self.parsers):
                break
        return self.mobj


class _ParserChainExample(ParserChain):
    def __init__(self):
        ParserChain.__init__(self)
        # chain of parsers [(section name, parser, postprocess, number of iterations)]
        self.parsers = [('Example', _ExamlpeParser(), self._example_after, '*')]

    def _example_after(self, mobj):
        if self.mobj is None:
            self.mobj = []
        self.mobj.append(mobj)
