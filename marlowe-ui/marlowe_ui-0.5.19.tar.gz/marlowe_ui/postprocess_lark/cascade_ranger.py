"""
parse output data from cascade/ranger.mfs
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common
from . import config

grammar = '''\
rngr_start:\
    (rngr_primary_escape | rngr_primary_ranges) rngr_primary_redisplaced?
rngr_primary_ranges: ELEM _S RNGR_TOK1 _NL\
    RNGR_TOK2 _S pfloat _S\
    RNGR_TOK3 _S pfloat _S\
    RNGR_TOK4 _S pfloat _S\
    RNGR_TOK5 _S pfloat _S\
    RNGR_TOK6 _S pfloat _NL
rngr_redisplaced: RNGR_TOK7 _NL
RNGR_TOK1: "Primary Recoil Ranges"
RNGR_TOK2: "Radial"
RNGR_TOK3: "Penetration"
RNGR_TOK4: "Spread"
RNGR_TOK5: "Total Path"
RNGR_TOK6: "Time (fs)"
RNGR_TOK7: "The primary was redisplaced"
rngr_primary_escape: _RNGR0700_1 _S ELEM _S "primary escaped through the" _S RNGR_SURFACE _S\
        "surface at" _S pfloat _S "fs" _NL
    _RNGR0700_1.100: "The"
    RNGR_SURFACE: "front" | "back" | "side" | "other"
rngr_primary_redisplaced: RNGR_TOK7 _NL
'''

grammer_join_list = [grammar, lark_common.grammar, lark_common.grammar_elem]

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

    def reset(self):
        pass

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def rngr_primary_ranges(self, args):
        '''cascade_ranger_primary_recoil_ranges:\
            ELEM
            RANGER_TOK1 _NL\
            RANGER_TOK2 _S
            pfloat _S\
            RANGER_TOK3 _S
            pfloat _S\
            RANGER_TOK4 _S
            pfloat _S\
            RANGER_TOK5 _S
            pfloat _S\
            RANGER_TOK6 _S
            pfloat _NL'''

        self.context.mobj['Elem'] = args[0]
        self.context.mobj['Recoil Range'] = {
                'Radial Range':args[3],
                'Penetration':args[5],
                'Spread':args[7],
                'Total Path':args[9],
                'Slowing Down Time':args[11]}

    def rngr_primary_escape(self, args):
        '''rngr_primary_escape: "The" _S
            ELEM _S "primary escaped through the" _S\
            RNGR_SURFACE _S "surface at" _S
            pfloat _S "fs" _NL'''
        self.context.mobj['Elem'] = args[0]
        self.context.mobj['Escape'] = {
                'Escape from':args[1].value,
                'Escape time':args[2]}

    def rngr_primary_redisplaced(self, args):
        self.context.mobj['Primary redisplaced'] = True

class Parser():
    def __init__(self, context, debug=False):
        self.context = context
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='rngr_start',
                debug=debug)

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
