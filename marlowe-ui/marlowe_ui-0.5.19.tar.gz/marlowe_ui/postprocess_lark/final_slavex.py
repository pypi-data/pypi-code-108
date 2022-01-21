"""
parse output data from final/slavex.mfs
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common

grammar = '''\
slvx_start: slvx_stat_anal slvx_rejected slvx_repeated slvx_timeorder slvx_encounter_prob\
    slvx_nondisp_collision slvx_vacancy_dist slvx_init_defect_dist?
'''

grammar_stat_anal = '''\
slvx_stat_anal:\
    slvx_stat_anal_head\
    (slvx_stat_anal_data | slvx_stat_anal_head)*

slvx_stat_anal_head: _SLVX5930_1 _S pint _S _SLVX5930_2 _NL _SLVX2200 _NL
slvx_stat_anal_data: TTLS_KNAME_2TO19 (_S pfloat)~6 _NL

_SLVX5930_1: "Statistical Analysis of Data from"
_SLVX5930_2: "Cascades"
_SLVX2200: ".....Total number of.....         Mean         Variance       Skewness       Kurtosis       Std Dev         Error"
'''

grammar_rejected = '''\
slvx_rejected: (slvx_rejected_invalid|slvx_rejected_valid)
slvx_rejected_invalid: _SLVX2200 _NL
slvx_rejected_valid:\
    slvx_rejected_valid_spec\
    slvx_rejected_valid_dist
slvx_rejected_valid_spec:\
    _SLVX2450 _NL\
    slvx_rejected_valid_spec_data+
slvx_rejected_valid_spec_data:\
    TTLS_LABEL_1TO4 (_S pint)~11 _NL
slvx_rejected_valid_dist:\
    _SLVX2580 _NL\
    slvx_rejected_valid_dist_data+
slvx_rejected_valid_dist_data:\
    TTLS_LABEL_1TO4 _S _SLVX5960_1 _S\
    pint _S _SLVX5960_2 _S\
    pint _S _SLVX5960_3 _S\
    pint _S _SLVX5960_4 _S\
    pint _NL\
    int_multiline_array15
_SLVX2450: "Targets rejected in SKATR: T/E Spectrum (channel width 0.1)                      Total"
_SLVX2580: "Distribution of Rejected-Target Numbers"
_SLVX5960_1: "Origin in channel"
_SLVX5960_2: "First channel reported"
_SLVX5960_3: "Channel width"
_SLVX5960_4: "Entries"
_SLVX2680: "No targets were rejected"
'''

grammar_repeated = '''\
slvx_repeated: (slvx_repeated_invalid | slvx_repeated_valid)
slvx_repeated_invalid: _SLVX2780 _NL
slvx_repeated_valid:\
    slvx_repeated_valid_dist\
    slvx_repeated_valid_numbers
slvx_repeated_valid_dist:\
    _SLVX6320_1 _NL\
    _SLVX6320_2 _NL\
    pint (_S pint)~10 _NL
slvx_repeated_valid_numbers:\
    _SLVX2840 _NL\
    _SLVX2850 _S _SLVX5960_1 _S\
    pint _S _SLVX5960_2 _S\
    pint _S _SLVX5960_3 _S\
    pint _S _SLVX5960_4 _S\
    pint _NL\
    int_multiline_array15

_SLVX6320_1: "Distribution of Repeated Target Searches"
_SLVX6320_2: "1         2         3         4         5              6         7         8         9        10+           Sum"
_SLVX2780: "There were no repeated target searches"
_SLVX2840: "Distribution of Repeated-Search Numbers"
_SLVX2850: "Cascade totals"
'''

grammar_timeorder = '''\
slvx_timeorder: slvx_timeorder_counts slvx_timeorder_hist
slvx_timeorder_counts:\
    _SLVX6020_1 _NL\
    _SLVX6020_2 _S pint _S _SLVX6020_3 _S pint _NL\
    _SLVX6020_4 _S pint _S _SLVX6020_5 _S pint _NL
_SLVX6020_1: "Analysis of Time Ordering"
_SLVX6020_2: "Misordered vacant sites"
_SLVX6020_3: "Misordered nonlattice targets"
_SLVX6020_4: "Ordered vacant sites"
_SLVX6020_5: "Ordered nonlattice targets"

slvx_timeorder_hist:\
    slvx_timeorder_hist_head\
    slvx_timeorder_hist_negative?\
    int_multiline_array10
slvx_timeorder_hist_head:\
    TTLS_TNAME_26 _NL\
    _SLVX6160_1 _S pfloat _S\
    _SLVX6160_2 _S pint _S\
    _SLVX6160_3 _S pint _S\
    _SLVX6160_4 _S pint _NL
slvx_timeorder_hist_negative: TTLS_LABEL_5 _S pint _NL

_SLVX6160_1: "Histogram scale (fs)"
_SLVX6160_2: "Origin in channel"
_SLVX6160_3: "First reported channel"
_SLVX6160_4: "Entries"
'''

grammar_encouter_prob = '''\
slvx_encounter_prob: slvx_encounter_prob_valid
?slvx_encounter_prob_valid:\
    slvx_encounter_prob_valid_head\
    slvx_encounter_prob_valid_data+

slvx_encounter_prob_valid_head:\
    _slvx_encounter_prob_valid_head_part
    | (_slvx_encounter_prob_valid_head_full+ _slvx_encounter_prob_valid_head_part?)

_slvx_encounter_prob_valid_head_full:\
    _SLVX3230 _NL _SLVX3240 (_S pint)~10 _NL
_slvx_encounter_prob_valid_head_part:\
     _SLVX3230 _NL _SLVX3240 (_S pint)~1..9 _NL

_SLVX3230: "Frequencies of Simultaneous Target and Vacancy Encounters"
_SLVX3240: "RB        Number of"

slvx_encounter_prob_valid_data:\
    slvx_encounter_prob_valid_data_lattice\
    slvx_encounter_prob_valid_data_nonlattice?\
    slvx_encounter_prob_valid_data_vacant?

slvx_encounter_prob_valid_data_lattice:\
    slvx_encounter_prob_valid_data_lattice_part\
    | (slvx_encounter_prob_valid_data_lattice_full+ slvx_encounter_prob_valid_data_lattice_part?)
slvx_encounter_prob_valid_data_lattice_full: pint _S TTLS_LABEL_6 (_S pint)~10 _NL\
    -> slvx_encounter_prob_valid_data_lattice_array
slvx_encounter_prob_valid_data_lattice_part: pint _S TTLS_LABEL_6 (_S pint)~1..9 _NL\
    -> slvx_encounter_prob_valid_data_lattice_array

slvx_encounter_prob_valid_data_nonlattice:\
    slvx_encounter_prob_valid_data_nonlattice_part\
    | (slvx_encounter_prob_valid_data_nonlattice_full+ slvx_encounter_prob_valid_data_nonlattice_part?)
slvx_encounter_prob_valid_data_nonlattice_full: TTLS_LABEL_7 (_S pint)~10 _NL\
    -> slvx_encounter_prob_valid_data_array
slvx_encounter_prob_valid_data_nonlattice_part: TTLS_LABEL_7 (_S pint)~1..9 _NL\
    -> slvx_encounter_prob_valid_data_array

slvx_encounter_prob_valid_data_vacant:\
    slvx_encounter_prob_valid_data_vacant_part\
    | (slvx_encounter_prob_valid_data_vacant_full+ slvx_encounter_prob_valid_data_vacant_part?)
slvx_encounter_prob_valid_data_vacant_full: TTLS_LABEL_8 (_S pint)~10 _NL\
    -> slvx_encounter_prob_valid_data_array
slvx_encounter_prob_valid_data_vacant_part: TTLS_LABEL_8 (_S pint)~1..9 _NL\
    -> slvx_encounter_prob_valid_data_array
'''

grammar_nondisp_collision = '''\
slvx_nondisp_collision:\
    slvx_nondisp_collision_head int_multiline_array15
slvx_nondisp_collision_head:\
    "Distribution of Sequences of Nondisplacive Collisions Occurring Above Replacement Threshold" _NL\
    "Total entries" _S pint _S "Origin in channel" _S pint _S "First reported channel" _S pint _S "Channel width" _S pint _NL
'''

grammar_vacancy_dist = '''\
slvx_vacancy_dist:\
    slvx_vacancy_dist_head int_multiline_array20
slvx_vacancy_dist_head:\
    "Cascade Vacancy Distribution" _NL\
    "Origin in channel" _S pint _S "First channel reported" _S pint _S "Channel width" _S pint _NL
'''

grammar_init_defect_dist = '''\
slvx_init_defect_dist:\
    slvx_init_defect_dist_head slvx_init_defect_dist_data+
slvx_init_defect_dist_head:\
    "Distribution of Initial Defect Sites and Atoms" _NL\
    "Cascades per Group:" fwint5 "          Group Channel Width:" fwint4 "          Groups:" fwint5 _NL
slvx_init_defect_dist_data:\
    TTLS_DNAME _S int_multiline_array10
        '''

grammer_join_list = [grammar,
        grammar_stat_anal,
        grammar_rejected,
        grammar_repeated,
        grammar_timeorder,
        grammar_encouter_prob,
        grammar_nondisp_collision,
        grammar_vacancy_dist,
        grammar_init_defect_dist,
        lark_common.grammar,
        lark_common.grammar_ttls_kname,
        lark_common.grammar_ttls_label,
        lark_common.grammar_ttls_tname,
        lark_common.grammar_ttls_dname,
        lark_common.grammar_fixedwidth_int]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = {}

class Transformer(lark_common.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.number_of_cascade = None

    def slvx_stat_anal_head(self, args):
        '''_SLVX5930_1 _S pint _S _SLVX5930_2 _NL _SLVX2200 _NL'''
        if self.number_of_cascade is None:
            self.number_of_cascade = args[0]
        else:
            assert self.number_of_cascade == args[0]

    def slvx_stat_anal_data(self, args):
        '''TTLS_KNAME_2TO19 (_S pfloat)~6 _NL'''
        return { 'label': args[0].value,
                    'Mean': args[1],
                    'Variance': args[2],
                    'Skewness': args[3],
                    'Kurtosis': args[4],
                    'Std Dev': args[5],
                    'Error': args[6]}

    def slvx_stat_anal(self, args):
        '''slvx_stat_anal:\
            slvx_stat_anal_head\
            (slvx_stat_anal_data | slvx_stat_anal_head)*'''
        data = [a for a in args if a]
        self.context.mobj['Statistical Analysis from Cascades'] = {
            'header': {'Number of Cascades': self.number_of_cascade},
            'data': data}

    def slvx_rejected_valid_spec_data(self, args):
        '''TTLS_LABEL_1TO4 (_S pint)~11 _NL'''
        return {args[0].value: {
            'header': {'Total': args[-1]},
            'data': args[1:-1]}}
        
    def slvx_rejected_valid_spec(self, args):
        '''_SLVX2450 _NL\
           slvx_rejected_valid_spec_data+'''
        obj = {}
        for v in args:
            obj.update(v)
        return {'Targets rejected in SKATR':obj}

    def slvx_rejected_valid_dist_data(self, args):
        '''TTLS_LABEL_1TO4 _S _SLVX5960_1 _S\
        pint _S _SLVX5960_2 _S\
        pint _S _SLVX5960_3 _S\
        pint _S _SLVX5960_4 _S\
        pint _NL\
        int_multiline_array15'''
        return {args[0].value: {
            'header': {
                'Origin in channel': args[1],
                'First channel reported': args[2],
                'Channel width': args[3],
                'Entries': args[4]},
            'data': args[5].children}}

    def slvx_rejected_valid_dist(self, args):
        '''_SLVX2580 _NL\
            slvx_rejected_valid_dist_data+'''
        obj = {}
        for v in args:
            obj.update(v)
        return {'Distribution of Rejected-Target Numbers':obj}

    def slvx_rejected(self, args):
        '''(slvx_rejected_invalid|slvx_rejected_valid)'''
        obj = {}
        if args[0].data == 'slvx_rejected_valid':
            for v in args[0].children:
                obj.update(v)
        self.context.mobj['Rejected Atom Histograms'] = obj

    def slvx_repeated_valid_dist(self, args):
        '''_SLVX6320_1 _NL\
            _SLVX6320_2 _NL\
            pint (_S pint)~10 _NL'''
        return {'Distribution of Repeated Target Searches': {
            'Sum': args[-1],
            'data': args[:-1]}}

    def slvx_repeated_valid_numbers(self, args):
        '''_SLVX2840 _NL _SLVX2850 _S _SLVX5960_1 _S\
        pint _S _SLVX5960_2 _S\
        pint _S _SLVX5960_3 _S\
        pint _S _SLVX5960_4 _S\
        pint _NL\
        int_multiline_array15'''
        return {'Distribution of Repeated-Search Numbers': {
            'Origin in channel': args[0],
            'First channel reported': args[1],
            'Channel width': args[2],
            'Entries': args[3],
            'data': args[4].children}}

    def slvx_repeated(self, args):
        '''(slvx_repeated_invalid|slvx_repeated_valid)'''
        obj = {}
        if args[0].data == 'slvx_repeated_valid':
            for v in args[0].children:
                obj.update(v)
        self.context.mobj['Repeated Search Histograms'] = obj


    def slvx_timeorder_counts(self, args):
        '''_SLVX6020_1 _NL\
        _SLVX6020_2 _S pint _S _SLVX6020_3 _S pint _NL\
        _SLVX6020_4 _S pint _S _SLVX6020_5 _S pint _NL'''
        return {
            'Time-ordering counts': {
                'Misordered vacant sites': args[0],
                'Misordered nonlattice targets': args[1],
                'Ordered vacant sites': args[2],
                'Ordered nonlattice targets': args[3]}}

    def slvx_timeorder_hist(self, args):
        '''slvx_timeorder_hist:\
            slvx_timeorder_hist_head\
            slvx_timeorder_hist_negative?\
            int_multiline_array10'''
        header = {
                'Histogram scale (fs)': args[0].children[1],
                'Origin in channel': args[0].children[2],
                'First reported channel': args[0].children[3],
                'Entries': args[0].children[4]}
        if args[1].data == 'slvx_timeorder_hist_negative':
            header['Negative time values'] = args[1].children[1]
        data = args[-1].children

        return {'Time Order of Collisions': {
            'header': header,
            'data': data}}

    def slvx_timeorder(self, args):
        obj = {}
        for v in args:
            if v:
                obj.update(v)
        self.context.mobj['Time Ordering'] = obj


    def slvx_encounter_prob_valid_head(self, args):
        return args
    
    def slvx_encounter_prob_valid(self, args):
        return {'header array': args[0], 'data': args[1:]}

    def slvx_encounter_prob_valid_data_lattice_array(self, args):
        '''slvx_encounter_prob_valid_data_lattice_part | slvx_encounter_prob_valid_data_lattice_full'''
        return {'RB': args[0], 'data': args[2:]}


    def slvx_encounter_prob_valid_data_array(self, args):
        return args[1:]


    def slvx_encounter_prob_valid_data_lattice(self, args):
        ary = []
        rb = None
        for a in args:
            if rb is None:
                rb = a['RB']
            else:
                assert(rb == a['RB'])
            ary.extend(a['data'])
        return {'RB': rb, 'Lattice targets': ary}


    def slvx_encounter_prob_valid_data_nonlattice(self, args):
        ary = []
        for a in args:
            ary.extend(a)
        return {'Nonlattice targets': ary}


    def slvx_encounter_prob_valid_data_vacant(self, args):
        ary = []
        for a in args:
            ary.extend(a)
        return {'Vacant lattice sites': ary}


    def slvx_encounter_prob_valid_data(self, args):
        obj = {}
        for a in args:
            obj.update(a)
        return obj

    def slvx_encounter_prob(self, args):
        if args[0]:
            self.context.mobj['Encounter Probabilities'] = args[0]


    def slvx_nondisp_collision(self, args):
        self.context.mobj['Nondisplacive Collision Spectrum'] = {
            'header': {
                'Total Entries':args[0].children[0],
                'Origin in channel':args[0].children[1],
                'First reported channel':args[0].children[2],
                'Channel width':args[0].children[3]},
            'data':args[1].children}


    def slvx_vacancy_dist(self, args):
        self.context.mobj['Cascade Vacancy Distribution'] = {
            'header': {
                'Origin in channel':args[0].children[0],
                'First channel reported':args[0].children[1],
                'Channel width':args[0].children[2]},
            'data':args[1].children}


    def slvx_init_defect_dist(self, args):
        '''
            slvx_init_defect_dist:\
                slvx_init_defect_dist_head slvx_init_defect_dist_data+
        '''
        self.context.mobj['Distribution of Initial Defect Sites and Atoms'] = {
                'header': args[0],
                'data': args[1:]}

    def slvx_init_defect_dist_head(self, args):
        '''"Distribution of Initial Defect Sites and Atoms" _NL\
            "Cascades per Group:" fwint5 "          Group Channel Width:" fwint4 "          Groups:" fwint5 _NL
        '''
        return {
                'Cascades per Group': args[0],
                'Group Channel Width': args[1],
                'Groups': args[2]}

    def slvx_init_defect_dist_data(self, args):
        '''TTLS_DNAME _S int_multiline_array10'''
        label = args[0].value
        data = args[1].children
        return {
                'header': {'label': label},
                'data': data}


class Parser():
    def __init__(self, context, debug=False):
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='slvx_start',
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
