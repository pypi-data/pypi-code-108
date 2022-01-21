"""
parse final/orgex.mfs output
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common

grammar = '''\
start: (orgx_header orgx_data+)+
orgx_header: ORGX_HEDZ _S "Pairs:" _S ORGX_HEDX _S "Distant" _S ORGX_HEAD _S\
        "Pair Separations (channel width" _S pfloat _S ")" _NL\
        "Channel       Mean          Variance        Skewness        Kurtosis        Std Dev          Error" _NL
orgx_data: pint (_S pfloat)~6 _NL

ORGX_HEDZ: "Proper" | "Improper"
ORGX_HEDX: "Correlated" | "Uncorrelated"
ORGX_HEAD: "Frenkel" | "Surface"
'''

grammer_join_list = [grammar, lark_common.grammar]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = {}

class Transformer(lark.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.current_title_key = None
        self.current_title = None
        self.current_channel_width = None

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def orgx_header(self, args):
        title_key = (args[0].value, args[1].value, args[2].value)
        channel_width = args[3]

        if self.current_title_key is None or self.current_title_key != title_key:
            self.current_title_key = title_key
            self.current_channel_width = channel_width
            self.current_title = f"{title_key[0]} Pairs: {title_key[1]} Distant {title_key[2]} Pair Separations"
            self.context.mobj[self.current_title] = {
                    'Channel width':channel_width,
                    'header': ['Channel', 'Mean', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev', 'Error'],
                    'data':[]}
        elif self.current_title_key == title_key:
            assert(self.current_channel_width == channel_width)

    def orgx_data(self, args):
        self.context.mobj[self.current_title]['data'].append(args)


class Parser():
    def __init__(self, context, debug=False):
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer, debug=debug)

    def parse(self, text):
        return self.parser.parse(text)


def parse(text, debug=False):
    '''parse input text and returns context object'''
    c = Context()
    parser = Parser(c, debug)
    parser.parse(text)
    return c.mobj


if __name__ == '__main__':
    import sys
    import argparse
    import io

    import pprint

    import logging

    logging.basicConfig(level=logging.INFO)

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input', type=argparse.FileType('rt'),
                        default=sys.stdin, nargs='?', help='input file')
    argparser.add_argument('output', type=argparse.FileType('wt'),
                        default=sys.stdout, nargs='?', help='output file')

    args = argparser.parse_args()


    context = Context()
    # prepare lark parser
    parser = Parser(context)

    # $EOF can be embedded for debugging
    buf = io.StringIO()
    for line in args.input:
        if line.startswith('$EOF'):
            buf.write('$EOF')
            break
        buf.write(line)

    # apply parsing
    result = parser.parse(buf.getvalue())

    # show lark object
    print(result.pretty())

    # show context
    pprint.pprint(context.mobj, compact=True, width=120)
