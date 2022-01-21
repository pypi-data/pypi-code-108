'''
parse 'cascade_report_summary' block
'''

import copy
import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common
from . import config

grammar = '''\
start:\
    summary_of_cascade\
    rejected_atoms\
    dist_repeated_target\
    time_order_analysis\
    frequencies+\
    nondisplacive?

// cascade/report.mfs RPRT4790
summary_of_cascade:\
    summary_of_cascade1\
    _SUMMARY_OF_CASCADE2\
    summary_of_cascade3
summary_of_cascade1: _SUMMARY_OF_CASCADE1_TOK1 int ":" _S "Group" int _S "Number" int _NL
    _SUMMARY_OF_CASCADE1_TOK1: "Summary of Cascade"
    _SUMMARY_OF_CASCADE1_TOK2: "Group"
    _SUMMARY_OF_CASCADE1_TOK3: "Number"
_SUMMARY_OF_CASCADE2: TTLS_KNAME_1 _S TTLS_KNAME_1 _NL
summary_of_cascade3:\
    TTLS_KNAME_2 int _NL\
    TTLS_KNAME_3 int _S TTLS_KNAME_4 int _NL\
    TTLS_KNAME_5 int _S TTLS_KNAME_6 int _NL\
    TTLS_KNAME_7 int _S TTLS_KNAME_8 int _NL\
    TTLS_KNAME_9 int _S TTLS_KNAME_10 int _NL\
    TTLS_KNAME_11 int _S TTLS_KNAME_12 int _NL\
    TTLS_KNAME_13 int _S TTLS_KNAME_14 int _NL\
    TTLS_KNAME_15 int _S TTLS_KNAME_16 int _NL\
    TTLS_KNAME_17 int _S TTLS_KNAME_18 int _NL\
    TTLS_KNAME_19 int _NL

// cascade/report.mfs RPRT0320
rejected_atoms: (_REJECTED_ATOMS1 rejected_atoms2*) | _REJECTED_ATOMS_NONE -> rejected_atoms
_REJECTED_ATOMS1: "Targets rejected in SKATR: T/E Spectrum (channel width 0.1)               Total" _NL
rejected_atoms2: TTLS_LABEL int~11 _NL
_REJECTED_ATOMS_NONE: "No targets were rejected" _NL

// cascade/report.mfs RPRT0450, RPRT5280
dist_repeated_target: dist_repeated_target1 | _DIST_REPEATED_TARGET2_TOK -> dist_repeated_target
dist_repeated_target1: _DIST_REPEATED_TARGET1_TOK int~11 _NL
_DIST_REPEATED_TARGET1_TOK:\
    "Distribution of Repeated Target Searches" _NL\
    "1         2         3         4         5              6         7         8         9        10+           Sum" _NL
_DIST_REPEATED_TARGET2_TOK: "There were no repeated target searches" _NL

// cascade/report.mfs RPRT0550
time_order_analysis:\
    time_order_analysis1 \
    time_order_analysis2 \
    time_order_analysis3?\
    time_order_analysis4 -> time_order_analysis
// cascade/report.mfs RPRT4850, RPRT0590
time_order_analysis1:\
    _TIME_ORDER_ANALYSIS1_TOK1 _NL\
    "Misordered vacant sites" int _S "Misordered nonlattice targets" int _NL\
    "Ordered vacant sites" int _S "Ordered nonlattice targets" int _NL
_TIME_ORDER_ANALYSIS1_TOK1: "Analysis of Time Ordering"
// cascade/report.mfs RPRT4920, RPRT0600
time_order_analysis2:\
    TTLS_TNAME_26 _NL\
    "Histogram scale (fs)" float "Origin in channel" int _S "First reported channel" int _S "Entries" int _NL
time_order_analysis3: TTLS_LABEL_5 int _NL
time_order_analysis4: int_multiline_array10

// cascade/report.mfs RPRT0860
frequencies: frequencies1 frequencies2+ -> frequencies
frequencies1:\
    _FREQUENCIES1_TOK1 _NL\
    _FREQUENCIES1_TOK2 int+ _NL
  _FREQUENCIES1_TOK1:"Frequencies of Simultaneous Target and Vacancy Encounters"
  _FREQUENCIES1_TOK2:"RB        Number of"
frequencies2: frequencies21 frequencies22? frequencies23?
frequencies21: int _S TTLS_LABEL_6 int+ _NL
frequencies22: TTLS_LABEL_7 int+ _NL
frequencies23: TTLS_LABEL_8 int+ _NL

// cascade/report.mfs RPRT1030 RPRT4880
nondisplacive:\
    _NONDISPLACIVE_TOK1 _NL\
    _NONDISPLACIVE_TOK2 int _S _NONDISPLACIVE_TOK3 int _S _NONDISPLACIVE_TOK4 _NL\
    int_multiline_array15 -> nondisplacive
    
    _NONDISPLACIVE_TOK1: "Distribution of Sequences of Nondisplacive Collisions Occurring Above Replacement Threshold"
    _NONDISPLACIVE_TOK2: "Total entries"
    _NONDISPLACIVE_TOK3: "Origin in Channel 0      First reported channel"
    _NONDISPLACIVE_TOK4: "Channel width 1"
'''

grammer_join_list = [
        grammar, lark_common.grammar,
        lark_common.grammar_ttls_kname,
        lark_common.grammar_ttls_tname,
        lark_common.grammar_ttls_label,
        lark_common.grammar_elem,
        ]

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

    def summary_of_cascade1(self, args):
        # summary_of_cascade1: _SUMMARY_OF_CASCADE1_TOK1
        # int ":" _S "Group"
        # int _S "Number"
        # int _NL
        obj = { 'Cascade':args[0], 'Group':args[1], 'Number':args[2]}
        return obj

    def summary_of_cascade3(self, args):
        # [Token(TTLS_KNAME_2, 'Collisions'), 18, ...]
        obj = dict(zip([a.value for a in args[0::2]], args[1::2]))
        return obj

    def summary_of_cascade(self, args):
        # summary_of_cascade:\
        #   summary_of_cascade1 _SUMMARY_OF_CASCADE2\
        #   summary_of_cascade3
        self.context.mobj = {}
        self.context.mobj.update(args[0])
        self.context.mobj['Total numbers'] = args[1]

    def dist_repeated_target(self, args):
        logger.debug(args)
        return args

    def rejected_atoms(self, args):
        logger.debug(args)
        return args

    def time_order_analysis(self, args):
        logger.debug(args)
        return args

    def frequencies(self, args):
        logger.debug(args)
        return args

    def nondisplacive(self, args):
        logger.debug(args)
        return args

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

    logging.basicConfig(level=logging.DEBUG)

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
