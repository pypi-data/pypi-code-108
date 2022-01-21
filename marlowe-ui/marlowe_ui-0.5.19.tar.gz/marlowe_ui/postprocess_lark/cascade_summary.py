'''
parse 'cascade_summary' block
'''

import copy
import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common
from . import config

grammar = '''\
start:\
    cascade\

// cascade/detail.mfs DETL2930
cascade:\
    "Cascade" fwint6 ":" _SS~5 "Group" fwint5 _SS~6 "Number" fwint3 _NL\
    "Polar Angle" _S pfloat _S "deg" _S "Azimuthal Angle" _S pfloat _S "deg" _NL\
    "Initial: Vacant Sites      Interstitials     Substitutions        Adatoms" _NL\
    pint (_S pint)~3 _NL
'''

grammer_join_list = [grammar, lark_common.grammar, lark_common.grammar_fixedwidth_int]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.reset()

    def reset(self):
        self.mobj = {}

class Transformer(lark_common.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.reset()

    def reset(self):
        pass

    def cascade(self, args):
        '''
            "Cascade" fwint6 ":" _SS~5 "Group" fwint5 _SS~6 "Number" fwint3 _NL\
            "Polar Angle" _S pfloat _S "deg" _S "Azimuthal Angle" _S pfloat _S "deg" _NL\
            "Initial: Vacant Sites      Interstitials     Substitutions        Adatoms" _NL\
            pint (_S pint)~3 _NL'''
        self.context.mobj = {
                'Index':{'Cascade':args[0], 'Group':args[1], 'Number':args[2]},
                'Initial':{
                    'Polar Angle':args[3], 'Azimuthal Angle':args[4],
                    'Initial Vacant Sites':args[5],
                    'Initial Interstitials':args[6],
                    'Initial Substitutions':args[7],
                    'Initial Adatoms':args[8]}
                }


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
    print(result.pretty())

    # show context
    pprint.pprint(context.mobj, compact=True, width=120)
