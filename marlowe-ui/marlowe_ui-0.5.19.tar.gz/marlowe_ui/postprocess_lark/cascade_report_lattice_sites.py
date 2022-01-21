"""
parse "Locations of the Cascade Lattice Sites" section

output routine is found at cascade/report.mfs:3830
"""

import lark

from . import lark_common
from . import config

import logging
logger = logging.getLogger(__name__)

grammar = '''\
start: (title header data+)+
title: "Locations of the Cascade Lattice Sites" _NL
header: "File    Site            ...........Location...........          Paired Atom" _NL
data: pint _S pint (_S pfloat)~3 _S pint _NL
'''

grammer_join_list = [grammar, lark_common.grammar]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.reset()

    def reset(self):
        self.mobj = {}

class Transformer(lark.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.reset()

    def reset(self):
        self.records = []

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def data(self, args):
        # data: pint _S pint (_S pfloat)~3 _S pint _NL
        #   'File':args[0],
        #   'Site':args[1],
        #   'Location X':args[2],
        #   'Location Y':args[3],
        #   'Location Z':args[4],
        #   'Paired Atom File':args[5]
        self.records.append(args)

    def start(self, args):
        self.context.mobj = self.records


class Parser():
    def __init__(self, context, debug=False):
        self.context = context
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer, debug=debug)

    def parse(self, text):
        return self.parser.parse(text)

    def reset(self):
        self.context.reset()
        self.transformer.reset()


_context = Context()
_parser = Parser(_context, debug=config.debug_module_parser)

def _parse_using_prebuild_parser(text, debug=False):
    '''parse input text and returns context object'''
    _parser.reset()
    _parser.parse(text)
    return _context.mobj

def _parse_using_ondemand_parser(text, debug=False):
    '''parse input text and returns context object'''
    c = Context()
    parser = Parser(c, debug)
    parser.parse(text)
    return c.mobj

parse = _parse_using_prebuild_parser if config.use_prebuild_parser else _parse_using_ondemand_parser


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
    # print(result.pretty())

    # show context
    pprint.pprint(context.mobj, compact=True, width=120)
