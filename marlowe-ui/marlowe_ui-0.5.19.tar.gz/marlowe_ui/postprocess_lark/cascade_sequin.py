"""
parse output data from cascade/sequin.mfs
"""

import lark

from . import lark_common
from . import config

import logging
logger = logging.getLogger(__name__)


grammar = '''\
seqn_start: seqn_focuson seqn_replacement
seqn_focuson: seqn_focuson_invalid | (seqn_focuson2 seqn_focuson3)
seqn_focuson_invalid: SEQN3060 _NL
seqn_focuson2:\
    SEQN4390 _NL\
    SEQN4410_1 _NL\
    SEQN4420_1 _NL\
    pint (_S pint)~8 _NL
seqn_focuson3:\
    SEQ4450_1 _NL\
    SEQ4460_1 _NL\
    pint (_S pint)~7 _NL

seqn_replacement: seqn_replacement_invalid | seqn_replacement_valid
seqn_replacement_invalid: SEQN3180 _NL
seqn_replacement_valid:\
    seqn_replacement2 seqn_replacement3 seqn_replacement_seq
seqn_replacement2:\
    SEQN4400 _NL\
    SEQN4410_2 _NL\
    SEQN4420_2 _NL\
    pint (_S pint)~8 _NL
seqn_replacement3:\
    SEQ4450_2 _NL\
    SEQ4460_2 _NL\
    pint (_S pint)~8 _NL

seqn_replacement_seq:\
    SEQN3320 _NL\
    SEQN3330 _S pfloat _NL\
    SEQN4310_1 _S SEQN4310_2 _S pint _S\
    SEQN4310_3 _S pint _S SEQN4310_4 _S pint SEQN4310_5 _S pint _NL\
    int_multiline_array20\
    seqn_replacement_large_miller?\
    seqn_replacement_seq_all?

seqn_replacement_large_miller:\
    "*****Replacement sequences with large Miller indices encountered" _NL\
    pint _SS "sequences have been omitted.  The maximum omitted length was" fwint5 _NL


seqn_replacement_seq_all:\
    seqn_replacement_seq_indeterminate_direction?\
    "All sequence directions are in external coordinates" _NL\
    seqn_replacement_seq_all_1?\
    seqn_replacement_seq_all_2+

seqn_replacement_seq_indeterminate_direction:\
    "Indeterminate directions are labelled <0, 0, 0>" _NL
seqn_replacement_seq_all_1:\
    "Equivalent directions are combined where possible" _NL
seqn_replacement_seq_all_2:\
    "<" fwint3 ":" seqn_narrow_3i3 ">" _S SEQN4310_2 fwint4 _SS~8 SEQN4310_3 fwint5 _SS~8 SEQN4310_4 fwint4 SEQN4310_5 fwint5 _NL\
    int_multiline_array20
seqn_narrow_3i3: /[ \\d\\*+-]+/

SEQN3060: "No focuson events were found"
SEQN3180: "No replacement events were found"
SEQN4390: "The Final States of 'Focuson' Sequences"
SEQN4400: "The Final States of Replacement Sequences"
SEQN4410: "Atoms Escaping from the Target Surfaces          Adatoms Trapped at Target Surfaces     "
SEQN4420: "Front        Back         Side         Other        Front        Back         Other       "

SEQN4410_1: SEQN4410 "Replace-      Close"
SEQN4420_1: SEQN4420 " ments        Pairs"
SEQN4410_2: SEQN4410 "Atoms in     Inter-"
SEQN4420_2: SEQN4420 "Focusons     rupted"

SEQ4450_1: "Linked to     Proper      Improper      Inter-       Forcibly    Cut Off in   Truncated"
SEQ4460_1: "Other Layer    Pairs        Pairs        stitial     Terminated     SINGLE     Sequences      'Lost'"
SEQ4450_2: "Large" " "~6 SEQ4450_1
SEQ4460_2: "Angle" " "~5 SEQ4460_1

SEQN3320: "Analysis of Replacement Sequences"
SEQN3330: "Straightness Control Parameter"
SEQN4310_1: "All Sequences"
SEQN4310_2: "First Channel"
SEQN4310_3: "Maximum Length"
SEQN4310_4: "Long Sequences (>"
SEQN4310_5: ")"
'''

grammer_join_list = [grammar, lark_common.grammar, lark_common.grammar_fixedwidth_int, lark_common.grammar_elem]

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

    def seqn_focuson1(self, args):
        return None

    def seqn_focuson2(self, args):
        '''seqn_focuson2:\
            SEQN4390 _NL\
            SEQN4410_1 _NL\
            SEQN4420_1 _NL\
            pint (_S pint)~8 _NL'''
        obj = {
                'Atoms Escaping from the Target Surfaces':{
                    'Front':args[3], 'Back':args[4], 'Side':args[5], 'Other':args[6]},
                'Addatoms Trapped at Target Surfaces':{
                    'Front':args[7], 'Back':args[8], 'Other':args[9]},
                'Replacements':args[10],
                'Close Pairs':args[11]}
        return obj

    def seqn_focuson3(self, args):
        '''seqn_focuson3:\
            SEQ4450_1 _NL\
            SEQ4460_1 _NL\
            pint (_S pint)~7 _NL'''
        obj = {
                'Linked to Other Layer':args[2],
                'Proper Pairs':args[3],
                'Improper Pairs':args[4],
                'Interstitial':args[5],
                'Forcibly Terminated':args[6],
                'Cut Off in SINGLE':args[7],
                'Truncated Sequences':args[8],
                'Lost':args[9]}
        return obj

    def seqn_focuson(self, args):
        if len(args) == 2:
            obj = {}
            obj.update(args[0])
            obj.update(args[1])
            return obj
        else:
            return None


    def seqn_replacement_invalid(self, args):
        return None

    def seqn_replacement2(self, args):
        '''seqn_replacement2:\
            SEQN4400 _NL\
            SEQN4410_2 _NL\
            SEQN4420_2 _NL\
            pint (_S pint)~8 _NL'''
        obj = {
                'Atoms Escaping from the Target Surfaces':{
                    'Front':args[3], 'Back':args[4], 'Side':args[5], 'Other':args[6]},
                'Addatoms Trapped at Target Surfaces':{
                    'Front':args[7], 'Back':args[8], 'Other':args[9]},
                'Atoms in Focusons':args[10],
                'Interrupted':args[11]}
        return obj

    def seqn_replacement3(self, args):
        '''seqn_replacement3:\
            SEQ4450_2 _NL\
            SEQ4460_2 _NL\
            pint (_S pint)~8 _NL'''
        obj = {
                'Large Angle':args[2],
                'Linked to Other Layer':args[3],
                'Proper Pairs':args[4],
                'Improper Pairs':args[5],
                'Interstitial':args[6],
                'Forcibly Terminated':args[7],
                'Cut Off in SINGLE':args[8],
                'Truncated Sequences':args[9],
                'Lost':args[10]}
        return obj

    def seqn_replacement_seq(self, args):
        '''seqn_replacement_seq:\
            SEQN3320 _NL\
            SEQN3330 _S
            pfloat _NL\
            SEQN4310_1 _S
            SEQN4310_2 _S
            pint _S\
            SEQN4310_3 _S
            pint _S
            SEQN4310_4 _S
            pint
            SEQN4310_5 _S
            pint _NL\
            int_multiline_array20\
            seqn_replacement_large_miller?\
            seqn_replacement_seq_all?
            '''
        obj = {
                'Analysis of Replacement Sequences':{
                    'Straightness Control Parameter':args[2],
                    'First Channel':args[5],
                    'Maximum Length':args[7],
                    'Long Sequence Threshold':args[9],
                    'Long Sequence Count':args[11],
                    'data':args[12].children}}
        # optional parts
        for a in args[13:]:
            obj['Analysis of Replacement Sequences'][a.data] = a.children
        # if len(args) > 13:
        #    obj['Analysis of Replacement Sequences']['All sequence'] = args[13]

        return obj

    def seqn_replacement_large_miller(self, args):
        '''
        "*****Replacement sequences with large Miller indices encountered" _NL\
        pint _SS "sequences have been omitted.  The maximum omitted length was" fwint5 _NL
        '''
        return lark.Tree('Large Miller indicies',
                {
                    'Omitted sequences': args[0],
                    'Maximum omitted length': args[1]
                    })


    def seqn_replacement_seq_all(self, args):
        '''
        seqn_replacement_seq_indeterminate_direction?\
        "All sequence directions are in external coordinates" _NL\
        seqn_replacement_seq_all_1?\
        seqn_replacement_seq_all_2+'''
        obj = {}
        if args[0].data == 'seqn_replacement_seq_indeterminate_direction':
            obj['Indeterminate directions are labelled'] = True
            args.pop(0)
        if args[0].data == 'seqn_replacement_seq_all_1':
            obj['Equivalent directions are combined where possible'] = True
            args.pop(0)
        obj['data'] = args[0:]
        return lark.Tree('All sequence', obj)


    def seqn_replacement_seq_all_2(self, args):
        ''' "<"
        fwint3 ":"
        seqn_narrow_3i3 ">" _S SEQN4310_2 _S
        pint _S SEQN4310_3 _S
        pint _S SEQN4310_4 _S
        pint SEQN4310_5 _S
        pint _NL\
        int_multiline_array20'''
        obj = {
                'Index': args[0],
                'Vector': args[1],
                'First Channel':args[3],
                'Maximum Length':args[5],
                'Long Sequence Threshold':args[7],
                'Long Sequence Count':args[9],
                'data':args[10].children}
        return obj

    def seqn_narrow_3i3(self, args):
        return self.parse_narrow_3I3(args[0])

    @staticmethod
    def parse_narrow_3I3(text):
        '''parse 3I3 format
        text: input text, which may be formatted in 3I3, or 3(X,I)
        return: [int, int, int]
        '''

        # first, simply split text with WS.
        sp = text.split()
        if len(sp) < 3:
            # assume some values are concatinated
            # it may consists '*', which shall be replaced to 9 (see, lark_common.gen_fixedwidth_int_reciever())
            sp = [text[i:i+3].replace('*', '9') for i in range(0, 9, 3)]
        elif len(sp) > 3:
            raise 'too match array elements'

        # str -> int
        return [int(s) for s in sp]


    def seqn_replacement_valid(self, args):
        obj = {}
        for a in args:
            obj.update(a)
        return obj

    def seqn_replacement(self, args):
        return args[0]

    def seqn_start(self, args):
        self.context.mobj['The Final States of \'Focuson\' Sequences'] = args[0]
        self.context.mobj['The Final States of Replacement Sequences'] = args[1]


class Parser():
    def __init__(self, context, debug=False):
        self.context = context
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='seqn_start',
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
