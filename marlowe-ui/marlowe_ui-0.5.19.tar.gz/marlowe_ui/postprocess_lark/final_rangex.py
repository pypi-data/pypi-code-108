"""
parse output data from final/rangex.mfs
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common

grammar = '''\
rngx_start:\
    rngx_primary_recoil_ranges\
    rngx_distribution_function\
    rngx_final_states_primary_recoil
'''

grammar_primary_recoil_ranges = '''\
rngx_primary_recoil_ranges: rngx_primary_recoil_ranges_valid | rngx_primary_recoil_ranges_invalid
rngx_primary_recoil_ranges_invalid: _RNGX0910 _NL
rngx_primary_recoil_ranges_valid:\
        _RNGX0840 _S pint _S _RNGX0850 _NL\
        _MOMX_LINE _NL\
        rngx_primary_recoil_ranges_data~5\
        ((_MOMX_LINE _NL)| rngx_primary_recoil_ranges_data)*
rngx_primary_recoil_ranges_data: RNGX_NAME _S pfloat (_S pfloat)~5 _NL

_RNGX0840: "Analysis of Primary Recoil Ranges ("
_RNGX0850: "Stopped Particles)"
_RNGX0910: "No primary recoils were stopped within the target"
_MOMX_LINE: TTLS_MOMX_1 _S TTLS_MOMX_2 _S TTLS_MOMX_3 _S TTLS_MOMX_4 _S TTLS_MOMX_5 _S TTLS_MOMX_6
RNGX_NAME: RNGX_NAME_1 | RNGX_NAME_2 | RNGX_NAME_3 | RNGX_NAME_4\
        | RNGX_NAME_5 | RNGX_NAME_6 | RNGX_NAME_7 | RNGX_NAME_8 | RNGX_NAME_9
RNGX_NAME_1: "Radial Range"
RNGX_NAME_2: "Penetration"
RNGX_NAME_3: "Spread"
RNGX_NAME_4: "Total Path"
RNGX_NAME_5: "Slowing Down Time"
RNGX_NAME_6: "Front Escape Time"
RNGX_NAME_7: "Back Escape Time"
RNGX_NAME_8: "Side Escape Time"
RNGX_NAME_9: "Other Escape Time"
'''

grammar_distribution_function = '''\
rngx_distribution_function: rngx_distribution_function_single*
rngx_distribution_function_single:\
    rngx_distribution_function_head\
    rngx_distribution_function_negative? \
    int_multiline_array15
rngx_distribution_function_head:\
    _RNGX2340_1 _S RNGX_NAME _NL\
    _RNGX2340_2 _S pfloat _S\
    _RNGX2340_3 _S pint _S\
    _RNGX2340_4 _S pint _RNGX2340_5 _NL
rngx_distribution_function_negative: _RNGX1190 _S pint _NL

_RNGX2340_1: "Distribution Function:"
_RNGX2340_2: "(Histogram channel width"
_RNGX2340_3: "Origin in Channel"
_RNGX2340_4: "First reported channel"
_RNGX2340_5: ")"
_RNGX1190: "Negative values:"
'''

grammar_final_states_primary_recoils = '''\
rngx_final_states_primary_recoil:\
    _RNGX1570 _NL\
    rngx_escaping_from_target_surfaces?\
    (_RNGX1570 _NL)?\
    rngx_proper_frenkel_pairs?\
    (_RNGX1570 _NL)?\
    rngx_proper_surface_pairs?\
    (_RNGX1570 _NL)?\
    rngx_improper_frenkel_pairs?\
    (_RNGX1570 _NL)?\
    rngx_improper_surface_pairs?

rngx_escaping_from_target_surfaces: _RNGX1580 _NL pint (_S pint)~9 _NL
rngx_proper_frenkel_pairs: _RNGX1690 _NL pint (_S pint)~9 _NL
rngx_proper_surface_pairs: _RNGX1820 _NL pint (_S pint)~8 _NL
rngx_improper_frenkel_pairs: _RNGX1940 _NL pint (_S pint)~8 _NL
rngx_improper_surface_pairs: _RNGX2070 _NL pint (_S pint)~8 _NL

_RNGX1570: "Final States of Primary Recoils"
_RNGX1580: _RNGX2370_1 _NL _RNGX2370_2
_RNGX2370_1: "Escaping from the Target Surfaces          Initial       Not         Trapped at Target Surfaces       Forcibly"
_RNGX2370_2: "Front       Back        Sides       Other     Focusons     Paired       Front       Back        Other    Terminated"

_RNGX1690: "Proper Frenkel Pairs" _NL _RNGX2410_1 _NL _RNGX2410_2
_RNGX2410_1: "Replace-     ...Close Pairs...       ...Near  Pairs...       ..Distant Pairs..       Other     Truncated   Truncated"
_RNGX2410_2: "ments       Corr       Uncorr       Corr       Uncorr       Corr       Uncorr       Pairs      Stenons    in SINGLE"

_RNGX1820: "Proper Surface Pairs" _NL _RNGX2450 _NL _RNGX2460 
_RNGX2450: ".........Close Pairs.........       .........Near  Pairs.........       ........Distant Pairs........"
_RNGX2460: "Front       Back        Other       Front       Back        Other       Front       Back        Other"

_RNGX1940: "Improper Frenkel Pairs" _NL _RNGX2410_3 _NL _RNGX2410_4
_RNGX2410_3: "Replace-     ...Close Pairs...       ...Near  Pairs...       ..Distant Pairs..       Other"
_RNGX2410_4: "ments       Corr       Uncorr       Corr       Uncorr       Corr       Uncorr       Pairs      'Lost'"

_RNGX2070: "Improper Surface Pairs" _NL _RNGX2450 _NL _RNGX2460 
'''


grammer_join_list = [grammar,
        grammar_primary_recoil_ranges,
        grammar_distribution_function,
        grammar_final_states_primary_recoils,
        lark_common.grammar, lark_common.grammar_ttls_momx]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = {}
    
class Transformer(lark.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def rngx_primary_recoil_ranges_data(self, args):
        '''RNGX_NAME _S
            pfloat (_S pfloat)~5 _NL'''
        return {
                args[0].value: {
                    'Mean': args[1],
                    'Variance': args[2],
                    'Skewness': args[3],
                    'Kurtosis': args[4],
                    'Std Dev': args[5],
                    'Error': args[6]}}

    def rngx_primary_recoil_ranges_valid(self, args):
        '''_RNGX0840 _S pint _S _RNGX0850 _NL _MOMX_LINE _NL
            rngx_primary_recoil_ranges_data~5\
            ((_MOMX_LINE _NL)| rngx_primary_recoil_ranges_data)*'''
        obj = {'Stopped Particles': args[0]}
        if len(args) > 1:
            for v in args[1:]:
                obj.update(v)
        return obj

    def rngx_primary_recoil_ranges_invalid(self, args):
        return {}

    def rngx_primary_recoil_ranges(self, args):
        self.context.mobj['Analysis of Primary Recoil Ranges'] = args[0]

    def rngx_distribution_function_single(self, args):
        '''rngx_distribution_function_head
           rngx_distribution_function_negative?
           rngx_distribution_function_data'''

        name = args[0].children[0].value

        obj = {
            'Histogram channel width': args[0].children[1],
            'Origin in Channel': args[0].children[2],
            'First reported channel': args[0].children[2]}
        if args[1].data == 'rngx_distribution_function_negative':
            obj['Negative values'] = args[1].children[0]
        obj['data'] = args[-1].children

        return {name:obj}

    def rngx_distribution_function(self, args):
        '''rngx_distribution_function_single*'''
        obj = {}
        for v in args:
            obj.update(v)
        self.context.mobj['Distribution Function'] = obj

    def rngx_escaping_from_target_surfaces(self, args):
        '''_RNGX1580 _NL pint (_S pint)~9 _NL'''
        return {
            'Escaping from the Target Surfaces': {
                'Front': args[0],
                'Back': args[1],
                'Sides': args[2],
                'Other': args[3]},
            'Initial Focusons': args[4],
            'Not Paired': args[5],
            'Trapped at Target Surfaces': {
                'Front': args[6],
                'Back': args[7],
                'Other': args[8]},
            'Forcibly Terminated': args[9]}

    def rngx_proper_frenkel_pairs(self, args):
        '''_RNGX1690 _NL pint (_S pint)~9 _NL'''
        return {
            'Proper Frenkel Pairs': {
                'Replacements': args[0],
                'Close Pairs': {
                    'Corr': args[1],
                    'Uncorr': args[2]},
                'Near Pairs': {
                    'Corr': args[3],
                    'Uncorr': args[4]},
                'Distant Pairs': {
                    'Corr': args[5],
                    'Uncorr': args[6]},
                'Other Pairs': args[7],
                'Truncated Stenons': args[8],
                'Trancated in SINGLE': args[9]}}

    def rngx_proper_surface_pairs(self, args):
        '''_RNGX1820 _NL pint (_S pint)~8 _NL'''
        return {
            'Proper Surface Pairs': {
                'Close Pairs': {
                    'Front': args[0],
                    'Back': args[1],
                    'Other': args[2]},
                'Near Pairs': {
                    'Front': args[3],
                    'Back': args[4],
                    'Other': args[5]},
                'Distant Pairs': {
                    'Front': args[6],
                    'Back': args[7],
                    'Other': args[8]}}}

    def rngx_improper_frenkel_pairs(self, args):
        '''_RNGX1940 _NL pint (_S pint)~8 _NL'''
        return {
            'Improper Frenkel Pairs': {
                'Replacements': args[0],
                'Close Pairs': {
                    'Corr': args[1],
                    'Uncorr': args[2]},
                'Near Pairs': {
                    'Corr': args[3],
                    'Uncorr': args[4]},
                'Distant Pairs': {
                    'Corr': args[5],
                    'Uncorr': args[6]},
                'Other Pairs': args[7],
                'Lost': args[8]}}

    def rngx_improper_surface_pairs(self, args):
        '''_RNGX2070 _NL pint (_S pint)~8 _NL'''
        return {
            'Improper Surface Pairs': {
                'Close Pairs': {
                    'Front': args[0],
                    'Back': args[1],
                    'Other': args[2]},
                'Near Pairs': {
                    'Front': args[3],
                    'Back': args[4],
                    'Other': args[5]},
                'Distant Pairs': {
                    'Front': args[6],
                    'Back': args[7],
                    'Other': args[8]}}}

    def rngx_final_states_primary_recoil(self, args):
        '''_RNGX1570 _NL\
        rngx_escaping_from_target_surfaces?\
        (_RNGX1570 _NL)?\
        rngx_proper_frenkel_pairs?\
        (_RNGX1570 _NL)?\
        rngx_proper_surface_pairs?\
        (_RNGX1570 _NL)?\
        rngx_improper_frenkel_pairs?\
        (_RNGX1570 _NL)?\
        rngx_improper_surface_pairs?'''
        obj = {}
        for v in args:
            obj.update(v)
        
        self.context.mobj['Final States of Primary Recoils'] = obj



class Parser():
    def __init__(self, context, debug=False):
        self.context = context
        self.transformer = Transformer(self.context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='rngx_start',
                debug=debug)

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

    # $EOF can be embedded for debugging
    buf = io.StringIO()
    for line in args.input:
        if line.startswith('$EOF'):
            buf.write('$EOF')
            break
        buf.write(line)

    # apply parsing
    result = parse(buf.getvalue())

    # show context
    pprint.pprint(result, compact=True, width=120)
