'''
parse 'cascade_detail_projectile' block
'''

import copy
import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common
from . import config

grammar = '''\
start:\
    proj_b_coll\
    files\

// cascade/detail.mfs DETL1760
proj_b_coll: _PROJ_B_COLL_TOK int _S\
    "(Segment" int ";   LRB =" int "; XIPAC =" _S? pfloat _S? ")" _NL -> projectile_before_collision
_PROJ_B_COLL_TOK: "Projectile Before Collision"

// cascade/detail.mfs DETL3040
files: _file1 _file2 _file3 _file4 -> files
_file1: "File   Atom   KARMA         ......Current Location.......               ..Current Direction Cosines..." _NL
_file2: pint _S ELEM _S pint (_S pfloat)~6 _NL
_file3: "Reference Lattice Site (Site" int ")" _S "Original Location (Site" int ")             Energy         Time" _NL
_file4: pfloat (_S pfloat)~7 _NL
'''

grammer_join_list = [
        grammar, lark_common.grammar, lark_common.grammar_elem]

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
        pass

    def int(self, args):
        return(int(args[0]))

    def float(self, args):
        return(float(args[0]))

    def projectile_before_collision(self, args):
        # proj_b_coll: _PROJ_B_COLL_TOK
        #   int _S "(Segment"
        #   int ";   LRB ="
        #   int "; XIPAC ="
        #   float ")" _NL -> projectile_before_collision
        obj = { 'Index': args[0],
                'Segment': args[1],
                'LRB': args[2],
                'XIPAC': args[3]}
        self.context.mobj = obj


    def files(self, args):
        '''file1: "File   Atom   KARMA         ......Current Location.......               ..Current Direction Cosines..." _NL
        pint _S
        ELEM _S
        pint
        (_S pfloat)~6 _NL "Reference Lattice Site (Site"
        int ")" _S "Original Location (Site"
        int ")             Energy         Time"
        pfloat (_S pfloat)~7 _NL'''
        self.context.mobj['File'] = {
                'Index': args[0],
                'Elem': args[1].value,
                'Karma': args[2],
                'Current Location': args[3:6],
                'Current Direction Cosines': args[6:9],
                'Reference Lattice Site Index': args[9],
                'Original Location Index': args[10],
                'Reference Lattice Site': args[11:14],
                'Original Location': args[14:17],
                'Energy': args[17],
                'Time': args[18]} 


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
