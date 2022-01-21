"""Parse 'Cascade Summary for (Elem) atom' section"""

import lark

import logging
logger = logging.getLogger(__name__)

from . import lark_common
from . import config

grammar = '''\
start:\
    rprt_atom_elem+
rprt_atom_elem:\
    cascade_summary_header number_data_subheader number_data_line\
    (cascade_summary_header | number_data_subheader | number_data_line)*\
    energy_data_subheader energy_data_line\
    (cascade_summary_header | energy_data_subheader | energy_data_line)*\
    time_order_histogram*\
    atoms_in_motion?\
    inverse_energy_histogram*\
    sputtered_energy_histogram*\
    final_energy_histogram*\
    binding_energy_histogram*\

// cascade/report.mfs RPRT4840
cascade_summary_header: CASCADE_SUMMARY_HEADER_TOK1 _S ELEM _S CASCADE_SUMMARY_HEADER_TOK2 _NL
  CASCADE_SUMMARY_HEADER_TOK1: "Cascade Summary for"
  CASCADE_SUMMARY_HEADER_TOK2: "atoms"
number_data_subheader: TTLS_HNAME_1TO4 (_S TTLS_HNAME_1TO4)? _NL
number_data_line: TTLS_NNAME _S pint (_S TTLS_NNAME _S pint)? _NL
energy_data_subheader: TTLS_HNAME_5 (_S TTLS_HNAME_5)? _NL
energy_data_line: TTLS_GNAME _S pfloat (_S TTLS_GNAME _S pfloat)? _NL

// time-order histogram cascade/report RPRT380
time_order_histogram:\
    time_order_histogram_title\
    time_order_histogram_legend\
    time_order_histogram_negative?\
    int_multiline_array15

time_order_histogram_title: ELEM _S TTLS_TNAME_1TO25 _NL
time_order_histogram_legend:\
    HIST_LEG_SCALE1 _S pfloat _S\
    HIST_LEG_ORIG fwint5 _S\
    HIST_LEG_FIRSTCHAN fwint5 _S\
    HIST_LEG_ENTRIES1 _S pint _NL
time_order_histogram_negative: TTLS_LABEL_5 _S pint _NL

TTLS_TNAME_1TO25:\
    TTLS_TNAME_1 | TTLS_TNAME_2 | TTLS_TNAME_3 | TTLS_TNAME_4 | TTLS_TNAME_5
    | TTLS_TNAME_6 | TTLS_TNAME_7 | TTLS_TNAME_8 | TTLS_TNAME_9 | TTLS_TNAME_10
    | TTLS_TNAME_11 | TTLS_TNAME_12 | TTLS_TNAME_13 | TTLS_TNAME_14 | TTLS_TNAME_15
    | TTLS_TNAME_16 | TTLS_TNAME_17 | TTLS_TNAME_18 | TTLS_TNAME_19 | TTLS_TNAME_20
    | TTLS_TNAME_21 | TTLS_TNAME_22 | TTLS_TNAME_23 | TTLS_TNAME_24 | TTLS_TNAME_25

// cascade/report.mfs RPRT2460 RPRT4940
atoms_in_motion:\
    atoms_in_motion_title\
    atoms_in_motion_legend\
    int_multiline_array15

atoms_in_motion_title: ELEM _S ATOMS_IN_MOTION_TITLE_TOK1 float ATOMS_IN_MOTION_TITLE_TOK2 _NL
    ATOMS_IN_MOTION_TITLE_TOK1: "atoms in motion at the end of each"
    ATOMS_IN_MOTION_TITLE_TOK2: "fs time interval"
atoms_in_motion_legend: HIST_LEG_ORIG int _S HIST_LEG_FIRSTCHAN int _NL

// cascade/report.mfs RPRT2570 RPRT4970
inverse_energy_histogram:\
    inverse_energy_histogram_title\
    inverse_energy_histogram_legend\
    int_multiline_array15
inverse_energy_histogram_title: ELEM _S TTLS_ENAME _NL
inverse_energy_histogram_legend:\
    HIST_LEG_SCALE2 float\
    HIST_LEG_FIRSTCHAN int _S\
    HIST_LEG_ENTRIES2 int _NL

// cascade/report.mfs RPRT2570 RPRT5000
sputtered_energy_histogram:\
    sputtered_energy_histogram_title\
    sputtered_energy_histogram_legend\
    int_multiline_array15
sputtered_energy_histogram_title: ELEM _S TTLS_ZNAME _NL
sputtered_energy_histogram_legend:\
    HIST_LEG_SCALE3 float\
    HIST_LEG_ORIG fwint5 _S\
    HIST_LEG_FIRSTCHAN int _S\
    HIST_LEG_ENTRIES2 int _NL

// cascade/report.mfs RPRT2810 RPRT5030
final_energy_histogram:\
    final_energy_histogram_title\
    final_energy_histogram_legend\
    int_multiline_array10
final_energy_histogram_title: ELEM _S TTLS_FNAME _NL
final_energy_histogram_legend: HIST_LEG_SCALE4 float HIST_LEG_ENTRIES2 int _NL

// cascade/report.mfs RPRT2930 RPRT5050
binding_energy_histogram:\
    binding_energy_histogram_title\
    binding_energy_histogram_legend\
    int_multiline_array10
binding_energy_histogram_title: ELEM _S TTLS_QNAME _NL
binding_energy_histogram_legend:\
    HIST_LEG_SCALE4 float\
    HIST_LEG_ORIG fwint5 _S\
    HIST_LEG_FIRSTCHAN fwint5 _S\
    HIST_LEG_ENTRIES1 _S pint _NL

HIST_LEG_SCALE1: "Histogram scale (fs)"
HIST_LEG_SCALE2: "Inverse channel width (eV)"
HIST_LEG_SCALE3: "Channel width"
HIST_LEG_SCALE4: "Channel width (eV)"
HIST_LEG_ORIG: "Origin in channel"
HIST_LEG_FIRSTCHAN: "First reported channel"
HIST_LEG_ENTRIES1: "Entries"
HIST_LEG_ENTRIES2: "Total entries"
'''

grammer_join_list = [
        grammar,
        lark_common.grammar,
        lark_common.grammar_fixedwidth_int,
        lark_common.grammar_elem,
        lark_common.grammar_ttls_hname, lark_common.grammar_ttls_tname,
        lark_common.grammar_ttls_nname, lark_common.grammar_ttls_gname, lark_common.grammar_ttls_zname,
        lark_common.grammar_ttls_fname, lark_common.grammar_ttls_qname,
        lark_common.grammar_ttls_ename, lark_common.grammar_ttls_label]

grammar = '\n'.join(grammer_join_list)


class Context():
    def __init__(self):
        self.reset()

    def reset(self):
        self.mobj = []


class Transformer(lark_common.Transformer):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.reset()

    def reset(self):
        self.current_elem_obj = None
        self.current_elem = None
        self.current_number_header = None
        self.current_energy_header = None

    def cascade_summary_header(self, args):
        # Tree(cascade_summary_header,
        #    [Token(CASCADE_SUMMARY_HEADER_TOK1, 'Cascade Summary for'),
        #            Token(__ANON_0, 'Si'),
        #            Token(CASCADE_SUMMARY_HEADER_TOK2, 'atoms')])
        elem = args[1].value
        if self.current_elem is None:
            self.current_elem = elem
            self.current_elem_obj = {'Elem':elem}
            self.context.mobj.append(self.current_elem_obj)
        elif self.current_elem == elem:
            return ('cascade_summary (duplicated)')
        else:
            # set new transformer context
            self.current_elem = elem
            self.current_elem_obj = {'Elem':elem}
            self.current_number_header = None
            self.current_energy_header = None
            self.context.mobj.append(self.current_elem_obj)
        return ('cascade_summary_header', elem)

    def number_data_subheader(self, args):
        # Tree(number_data_subheader,
        #   [Token(TTLS_HNAME_1TO4, '.....Number of.....'),
        #    Token(TTLS_HNAME_1TO4, '.....Number of.....')])
        if len(args) > 1:
            assert args[0].value == args[1].value
        # pickup dict key assume '.'*5 + word + '.'*5
        self.current_number_header = args[0][5:-5]
        self.current_elem_obj.setdefault(self.current_number_header, {})

        # return ('cascade_summary_header', self.current_number_header)

    def number_data_line(self, args):
        # Tree(number_data_line,
        #   [Token(TTLS_NNAME, 'Atoms involved'),
        #    33,
        #    Token(TTLS_NNAME, 'Collisions'),
        #    114])
        for k, v in zip(args[0::2], args[1::2]):
            self.current_elem_obj[self.current_number_header][k.value] = v

    def energy_data_subheader(self, args):
        # Tree(energy_data_subheader, [
        #   Token(TTLS_HNAME_5, '.....Energy (eV).....'),
        #   Token(TTLS_HNAME_5, '.....Energy (eV).....')])
        if len(args) > 1:
            assert args[0].value == args[1].value
        # pickup dict key assume '.'*5 + word + '.'*5
        self.current_energy_header = args[0][5:-5]
        self.current_elem_obj.setdefault(self.current_energy_header, {})

        # return ('cascade_summary_header', self.current_energy_header)

    def energy_data_line(self, args):
        # Tree(energy_data_line, [
        #    Token(TTLS_GNAME, 'Inelastic energy loss'),
        #    52.1934, Token(TTLS_GNAME, 'Binding loss (displacements)'),
        #    112.0])
        for k, v in zip(args[0::2], args[1::2]):
            self.current_elem_obj[self.current_energy_header][k.value] = v

    def time_order_histogram_title(self, args):
        # Tree(time_order_histogram_title, [
        #   Token(ELEM, 'Si'),
        #   Token(TTLS_TNAME_1TO25, 'displaced atoms: initial time distribution')])
        elem = args[0].value
        assert self.current_elem == elem
        # self.current_time_order_histogram_title = args[1].value
        return args[1].value

    def time_order_histogram_legend(self, args):
        # Tree(time_order_histogram_legend, [
        #   Token(TIME_ORDER_HIST_LEG_TOK1, 'Histogram scale (fs)'),
        #   2.5,
        #   Token(TIME_ORDER_HIST_LEG_TOK2, 'Origin in channel'),
        #   1,
        #   Token(TIME_ORDER_HIST_LEG_TOK3, 'First reported channel'),
        #   1, Token(TIME_ORDER_HIST_LEG_TOK4, 'Entries'),
        #   30]
        # self.current_time_order_histogram_legend_scale = args[1].value
        # self.current_time_order_histogram_legend_origin = args[3].value
        # self.current_time_order_histogram_legend_first = args[5].value
        # self.current_time_order_histogram_legend_entries = args[7].value
        return (args[1], args[3], args[5], args[7])

    def time_order_histogram(self, args):
        # Tree(time_order_histogram, [
        #   'displaced atoms: initial time distribution',
        #    (2.5, 1, 1, 30),
        #   Tree(int_multiline_array15,
        #       [1, 0, 1, 0, ... ])])
        self.current_elem_obj.setdefault('Time order histogram', {})
        self.current_elem_obj['Time order histogram'][args[0]] = {
                'Histogram scale (fs)': args[1][0],
                'Origin in channel': args[1][1],
                'First reported channel': args[1][2],
                'Entries': args[1][3],
                'data': args[2].children}

    def atoms_in_motion_title(self, args):
        # Tree(atoms_in_motion_title, [
        #   Token(ELEM, 'Si'),
        #   Token(ATOMS_IN_MOTION_TITLE_TOK1, 'atoms in motion at the end of each'),
        #   2.5,
        #   Token(ATOMS_IN_MOTION_TITLE_TOK2, 'fs time interval')])
        elem = args[0].value
        assert self.current_elem == elem
        # self.atom_in_motion_time_interval = args[2]
        return args[2]
        
    def atoms_in_motion_legend(self, args):
        # Tree(atoms_in_motion_legend, [
        #   Token(HIST_LEG_ORIG, 'Origin in channel'),
        #   1,
        #   Token(HIST_LEG_FIRSTCHAN, 'First reported channel'),
        #   1])
        # origin = args[1].value
        # first = args[3].value
        return (args[1], args[3])

    def atoms_in_motion(self, args):
        # Tree(atoms_in_motion, [
        #   2.5,
        #   (1, 1),
        #   Tree(int_multiline_array15, [1, 1, 2, ...])])

        self.current_elem_obj['Atoms in motion histogram'] = {
                'time interval': args[0],
                'Origin in channel': args[1][0],
                'First reported channel': args[1][1],
                'data': args[2].children}


    def inverse_energy_histogram_title(self, args):
        # Tree(inverse_energy_histogram_title, [
        #   Token(ELEM, 'Si'),
        #   Token(TTLS_ENAME, 'atoms: initial inverse energy distribution')])
        elem = args[0].value
        assert self.current_elem == elem
        # self.current_inverse_energy_histogram_title = args[1].value
        return args[1].value

    def inverse_energy_histogram_legend(self, args):
        # Tree(inverse_energy_histogram_legend, [
        #   Token(INVERSE_ENERGY_HIST_LEG_TOK1, 'Inverse channel width (eV)'),
        #   450.0,
        #   Token(HIST_LEG_FIRSTCHAN, 'First reported channel'),
        #   1,
        #   Token(HIST_LEG_ENTRIES2, 'Total entries'),
        #   33])
        # self.current_inverse_energy_histogram_legend_scale = args[1].value
        # self.current_inverse_energy_histogram_legend_origin = args[3].value
        # self.current_inverse_energy_histogram_legend_first = args[5].value
        # self.current_inverse_energy_histogram_legend_entries = args[7].value
        return (args[1], args[3], args[5])

    def inverse_energy_histogram(self, args):
        # Tree(inverse_energy_histogram, [
        #   'atoms: initial inverse energy distribution',
        #   (450.0, 1, 33),
        #   Tree(int_multiline_array15, [1, 1, 0, ..., ])])
        self.current_elem_obj.setdefault('Inverse energy histogram', {})
        self.current_elem_obj['Inverse energy histogram'][args[0]] = {
                'Inverse channel width (eV)': args[1][0],
                'Origin in channel': args[1][1],
                'First reported channel': args[1][2],
                'data': args[2].children}

    def sputtered_energy_histogram_title(self, args):
        # Tree(sputtered_energy_histogram_title, [
        #   Token(ELEM, 'Si'),
        #   Token(TTLS_ZNAME, 'atoms sputtered from front surface: energy spectrum')])
        elem = args[0].value
        assert self.current_elem == elem
        # _title = args[1].value
        return args[1].value

    def sputtered_energy_histogram_legend(self, args):
        # Tree(sputtered_energy_histogram_legend, [
        #   Token(SPUTTERED_ENERGY_HIST_LEG_TOK1, 'Channel width'),
        #   1.125,
        #   Token(HIST_LEG_ORIG, 'Origin in channel'),
        #   1,
        #   Token(HIST_LEG_FIRSTCHAN, 'First reported channel'),
        #   18,
        #   Token(HIST_LEG_ENTRIES2, 'Total entries'),
        #   1])
        # _scale = args[1].value
        # _origin = args[3].value
        # _first = args[5].value
        # _entries = args[7].value
        return (args[1], args[3], args[5], args[7])

    def sputtered_energy_histogram(self, args):
        # Tree(sputtered_energy_histogram, [
        #   'atoms sputtered from front surface: energy spectrum',
        #   (1.125, 1, 18, 1),
        #   Tree(int_multiline_array15, [1])])
        self.current_elem_obj.setdefault('Sputtered energy histogram', {})
        self.current_elem_obj['Sputtered energy histogram'][args[0]] = {
                'Channel width': args[1][0],
                'Origin in channel': args[1][1],
                'First reported channel': args[1][2],
                'Total entries': args[1][3],
                'data': args[2].children}

    def final_energy_histogram_title(self, args):
        # final_energy_histogram_title: ELEM _S TTLS_FNAME _NL
        elem = args[0].value
        assert self.current_elem == elem
        # _title = args[1].value
        return args[1].value

    def final_energy_histogram_legend(self, args):
        # final_energy_histogram_legend:
        #   FINAL_ENERGY_HIST_LEG_TOK1
        #   float
        #   HIST_LEG_ENTRIES2
        #   int _NL
        return (args[1], args[3])

    def final_energy_histogram(self, args):
        # final_energy_histogram_title
        # final_energy_histogram_legend
        # int_multiline_array10
        self.current_elem_obj.setdefault('Final energy histogram', {})
        self.current_elem_obj['Final energy histogram'][args[0]] = {
                'Channel width': args[1][0],
                'Total entries': args[1][1],
                'data': args[2].children}

    def binding_energy_histogram_title(self, args):
        # binding_energy_histogram_title: ELEM _S TTLS_QNAME _NL
        elem = args[0].value
        assert self.current_elem == elem
        # _title = args[1].value
        return args[1].value

    def binding_energy_histogram_legend(self, args):
        # binding_energy_histogram_legend:
        #   HIST_LEG_SCALE4("Channel width (eV)")
        #   float
        #   HIST_LEG_ORIG("Origin in channel")
        #   int _S
        #   HIST_LEG_FIRSTCHAN("First reported channel")
        #   int _S
        #   HIST_LEG_ENTRIES1("Entries")
        #   int _NL
        return (args[1], args[3], args[5], args[7])

    def binding_energy_histogram(self, args):
        # binding_energy_histogram_title
        # binding_energy_histogram_legend
        # int_multiline_array10
        self.current_elem_obj.setdefault('Binding energy histogram', {})
        self.current_elem_obj['Binding energy histogram'][args[0]] = {
                'Channel width (eV)': args[1][0],
                'Origin in channel': args[1][1],
                'First reported channel': args[1][2],
                'Entries': args[1][3],
                'data': args[2].children}

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
