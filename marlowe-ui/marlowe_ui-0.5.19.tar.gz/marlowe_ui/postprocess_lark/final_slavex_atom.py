"""
parse output data from final/slavex.mfs (for each atom)
"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common

grammar = '''\
slvxa_start: slvxa_elem+
slvxa_elem: slvxa_stat slvxa_histo
slvxa_stat: slvxa_stat_number slvxa_stat_energy 
'''

grammar_stat = '''\
slvxa_stat_number:\
    slvxa_stat_head\
    slvxa_stat_number_head\
    slvxa_stat_number_data\
    (slvxa_stat_head | slvxa_stat_number_head | slvxa_stat_number_data)*

slvxa_stat_head: "Statistical Analysis of Data for" _S ELEM _S "Atoms in" _S pint _S "Cascades" _NL
slvxa_stat_number_head: TTLS_HNAME_1TO4 _S TTLS_MOMX _NL
slvxa_stat_number_data: TTLS_NNAME (_S pfloat)~6 _NL

slvxa_stat_energy:\
    slvxa_stat_energy_head\
    slvxa_stat_energy_data\
    (slvxa_stat_head | slvxa_stat_energy_head | slvxa_stat_energy_data)*
slvxa_stat_energy_head: TTLS_HNAME_5 _S TTLS_MOMX _NL
slvxa_stat_energy_data: TTLS_GNAME (_S pfloat)~6 _NL
'''

grammar_histo = '''\
slvxa_histo:\
    slvxa_histo_timescale*\
    slvxa_histo_moving_particle?\
    slvxa_histo_inv_energy*\
    slvxa_histo_sputtered_energy*\
    slvxa_histo_final_energy*\
    slvxa_histo_binding_energy*

slvxa_histo_timescale:\
    slvxa_histo_timescale_head\
    int_multiline_array15

// SLVX2960
slvxa_histo_timescale_head:\
    ELEM _S TTLS_TNAME _NL\
    "Histogram scale (fs)" _S pfloat _S\
    "Origin in channel" fwint5 _S\
    "First reported channel" fwint5 _S\
    "Entries" _S pint _NL

slvxa_histo_moving_particle:\
    slvxa_histo_moving_particle_head\
    int_multiline_array15

slvxa_histo_moving_particle_head:\
    ELEM _S "atoms in motion at the end of each" _S pfloat _S "fs time interval" _NL\
    "Origin in channel" _S pint _S\
    "First reported channel" _S pint _NL

slvxa_histo_inv_energy:\
    slvxa_histo_inv_energy_head\
    int_multiline_array15

// SLAVX5300
slvxa_histo_inv_energy_head:\
    ELEM _S TTLS_ENAME _NL\
    "Inverse channel width (eV)" _S pfloat _S\
    "First reported channel" _S pint _S\
    "Total entries" _S pint _NL

slvxa_histo_sputtered_energy:\
    slvxa_histo_sputtered_energy_head\
    int_multiline_array15

// SLVX6240
slvxa_histo_sputtered_energy_head:\
    ELEM _S TTLS_ZNAME _NL\
    "Channel width" _S pfloat _S\
    "Origin in channel" fwint5 _S\
    "First reported channel" _S pint _S\
    "Total entries" _S pint _NL

slvxa_histo_final_energy:\
    slvxa_histo_final_energy_head\
    int_multiline_array10

// SLVX5530
slvxa_histo_final_energy_head:\
    ELEM _S TTLS_FNAME _NL\
    "Channel width (eV)" _S pfloat _S\
    "Total entries" _S pint _NL

slvxa_histo_binding_energy:\
    slvxa_histo_binding_energy_head\
    int_multiline_array10

// SLVX6290
slvxa_histo_binding_energy_head:\
    ELEM _S TTLS_QNAME _NL\
    "Channel width (eV)" _S pfloat _S\
    "Origin in channel" fwint5 _S\
    "First reported channel" fwint5 _S\
    "Entries" _S pint _NL
'''

grammer_join_list = [grammar,
        grammar_stat,
        grammar_histo,
        lark_common.grammar,
        lark_common.grammar_fixedwidth_int,
        lark_common.grammar_elem,
        lark_common.grammar_ttls_momx,
        lark_common.grammar_ttls_hname,
        lark_common.grammar_ttls_nname,
        lark_common.grammar_ttls_gname,
        lark_common.grammar_ttls_tname,
        lark_common.grammar_ttls_ename,
        lark_common.grammar_ttls_zname,
        lark_common.grammar_ttls_fname,
        lark_common.grammar_ttls_qname,
        ]

grammar = '\n'.join(grammer_join_list)

class Context():
    def __init__(self):
        self.mobj = []

class Transformer(lark_common.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.elem = None
        self.cascades = None
        self.current_hname = None

    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])

    def slvxa_stat_head(self, args):
        elem = args[0].value
        cascades = args[1]
        if self.elem is None or self.elem != elem:
            # assume self.cascade is also None
            self.elem = elem
            self.cascades = cascades
            self.elem_obj = {
                    'Elem': self.elem,
                    'Cascades': self.cascades,
                    'Statistics': {},
                    'Histogram': {}} 
            self.context.mobj.append(self.elem_obj)

    def slvxa_stat_number_head(self, args):
        # remove head and tail '.'*5
        self.current_hname = args[0].value[5:-5]
        self.elem_obj['Statistics'].setdefault(self.current_hname, {})

    def slvxa_stat_number_data(self, args):
        self.elem_obj['Statistics'][self.current_hname][args[0].value] = {
                'Mean':args[1],
                'Variance':args[2],
                'Skewness':args[3],
                'Kurtosis':args[4],
                'Std Dev':args[5],
                'Error':args[6]}

    def slvxa_stat_energy_head(self, args):
        # remove head and tail '.'*5
        self.current_hname = args[0].value[5:-5]
        self.elem_obj['Statistics'].setdefault(self.current_hname, {})

    def slvxa_stat_energy_data(self, args):
        self.elem_obj['Statistics'][self.current_hname][args[0].value] = {
                'Mean':args[1],
                'Variance':args[2],
                'Skewness':args[3],
                'Kurtosis':args[4],
                'Std Dev':args[5],
                'Error':args[6]}

    def slvxa_histo_timescale(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram'][head.children[1].value] = {
                "Histogram scale (fs)":head.children[2],
                "Origin in channel":head.children[3],
                "First reported channel":head.children[4],
                "Entries":head.children[5],
                "data":data.children}

    def slvxa_histo_moving_particle(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram']['moving-particle time function'] = {
                "Time interval (fs)":head.children[1],
                "Origin in channel":head.children[2],
                "First reported channel":head.children[3],
                "data":data.children}

    def slvxa_histo_inv_energy(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram'][head.children[1].value] = {
                "Inverse channel width (eV)":head.children[2],
                "First reported channel":head.children[3],
                "Total entries":head.children[4],
                "data":data.children}

    def slvxa_histo_sputtered_energy(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram'][head.children[1].value] = {
                "Channel width":head.children[2],
                "Origin in channel":head.children[3],
                "First reported channel":head.children[4],
                "Total entries":head.children[5],
                "data":data.children}

    def slvxa_histo_final_energy(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram'][head.children[1].value] = {
                "Channel width (eV)":head.children[2],
                "Total entries":head.children[3],
                "data":data.children}

    def slvxa_histo_binding_energy(self, args):
        head = args[0]
        data = args[1]
        assert(head.children[0] == self.elem)
        self.elem_obj['Histogram'][head.children[1].value] = {
                "Channel width (eV)":head.children[2],
                "Origin in channel":head.children[3],
                "First reported channel":head.children[4],
                "Entries":head.children[5],
                "data":data.children}

class Parser():
    def __init__(self, context, debug=False):
        self.transformer = Transformer(context)
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='slvxa_start',
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
