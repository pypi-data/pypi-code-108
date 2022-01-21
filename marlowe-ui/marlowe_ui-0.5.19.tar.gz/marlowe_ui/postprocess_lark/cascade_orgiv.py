"""
parse output data from cascade/orgiv.mfs
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import config

from . import lark_common


grammar = '''\
orgv_start: (_orgv_valid | orgv_invalid)
_orgv_valid:\
    (_ORGV1840 _NL\
    _ORGV1850 _S _ORGV1850 _NL\
    _ORGV1860 _S _ORGV1860 _NL\
    orgv_multielem)+
orgv_invalid: _ORGV0720 _NL
orgv_elem: pint _S pint _S pint _S ELEM _S pint _S pfloat
orgv_multielem: (orgv_elem _S orgv_elem _NL)* (orgv_elem _NL)?

_ORGV0720: "No distant vacancy-interstitial pairs found"
_ORGV1840: "Separations of Distant Interstitial-Vacancy Pairs"
_ORGV1850: "Pair      Vacancy     Interstitial    Separation"
_ORGV1860: "Number   Site   File   Atom    File     Distance"
'''

grammer_join_list = [grammar, lark_common.grammar, lark_common.grammar_elem]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = {}

    def reset(self):
        self.mobj = {}


class Transformer(lark.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.reset()

    def reset(self):
        pass

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def orgv_elem(self, args):
        '''orgv_elem:
            pint _S
            pint _S
            pint _S
            ELEM _S
            pint _S
            pfloat'''
        # return {
        #         'Pair Number': args[0],
        #         'Vacancy Site': args[1],
        #         'Vacancy File': args[2],
        #         'Interstitial Atom': args[3].value,
        #         'Interstitial File': args[4],

        args[3] = args[3].value
        return args


    def orgv_multielem(self, args):
        return args

    def orgv_invalid(self, args):
        return None

    def orgv_start(self, args):
        if args[0] is None:
            self.context.mobj['status'] = 'invalid'
        else:
            self.context.mobj['status'] = 'valid'
            self.context.mobj['records'] = []
            for a in args:
                self.context.mobj['records'].extend(a)

class Parser():
    def __init__(self, context, debug=False):
        self.context = context
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='orgv_start',
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
