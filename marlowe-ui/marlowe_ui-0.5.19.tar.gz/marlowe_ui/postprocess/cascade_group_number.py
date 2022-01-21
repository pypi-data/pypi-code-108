"""
Parse 'cascade   \d+:  Group   \d+ Number \d+' section
This is a begininng of cascade detail
"""

import re
import functools
import math

from .abstractparser import testframe
from .parserchain import ParserChain
from . import summary_of_cascade
from . import cascade_summary_each_atom
from . import detailed_description_of_the_cascade_1
from . import detailed_description_of_the_cascade_2
from . import detailed_description_of_the_cascade_3
from . import location_of_the_cascade_lattice_sites
from . import primary_recoil_ranges
from . import separations_of_distant_iv_pairs


class Parser(ParserChain):
    def __init__(self):
        ParserChain.__init__(self)
        # fieldname and parser
        self.summary_of_cascade = summary_of_cascade.Parser()
        self.separations_of_distant_iv_pairs = separations_of_distant_iv_pairs.Parser()

        # (section name, parser, postprocess, number of iterations)
        self.parsers = [
            ('Summary of Cascade', self.summary_of_cascade,
                self.summary_of_cascade_after, 1),
            ('Cascade Summary for each Atom', cascade_summary_each_atom.Parser(),
                self.cascade_summary_each_atom_after, '*'),
            ('Cascade1', detailed_description_of_the_cascade_1.Parser(),
                self.after_setdict('Cascade Detail'), 1),
            ('Cascade2', detailed_description_of_the_cascade_2.Parser(),
                self.after_setdict('Cascade2'), 1),
            ('Cascade3', detailed_description_of_the_cascade_3.Parser(),
                self.after_setdict('Cascade3'), 1),
            ('Lattice Sites', location_of_the_cascade_lattice_sites.Parser(),
                self.after_setdict('Lattice Sites'), 1),
            ('Primary Recoil Ranges', primary_recoil_ranges.Parser(),
                self.after_setdict('Primary Recoil Ranges'), 1),
            ('Separations of Distant I-V Pairs', self.separations_of_distant_iv_pairs,
                self.after_setdict('Separations of Distant I-V Pairs'), 1)]

    # default action when parser returns a parsed object, this is callded as after in the parser
    def _after_setdict_base(self, key, mobj):
        """do self.mboj[key] = mobj
        """
        self.mobj[key] = mobj

    def after_setdict(self, key):
        return functools.partial(self._after_setdict_base, key)

    def summary_of_cascade_after(self, mobj):
        """Action when self.summary_of_cascade is finishded successfully

        mobj is parsed object
        """
        # set pairs attribut of seperations_of_distant_iv_pairs
        self.separations_of_distant_iv_pairs.pairs = mobj['Pairs identified']
        self.mobj['Summary of Cascade'] = mobj

    def cascade_summary_each_atom_after(self, mobj):
        """Action when self.summary_of_cascade is finishded successfully

        mobj is parsed object
        """
        # set pairs attribut of seperations_of_distant_iv_pairs
        mobj['Index'] = self.parser_multiplicity
        if 'Cascade Summary for each Atom' not in self.mobj:
            self.mobj['Cascade Summary for each Atom'] = []
        self.mobj['Cascade Summary for each Atom'].append(mobj)

    # see cascade/detail.mfs DETL2930 
    # 60 FORMAT(6X,38X,'Cascade',I6,':',5X,'Group',I5,6X,'Number',I3//6X,18DETL2930
    #   1X,'Polar Angle',G14.6,' deg',22X,'Azimuthal Angle',G14.6,' deg'//6DETL2940
    #   2X,23X,'Initial: Vacant Sites',6X,'Interstitials',5X,'SubstitutionsDETL2950
    #   3',8X,'Adatoms'/6X,22X,4I18)					DETL2960
    #
    strippedtitle_re = re.compile(
        r'Cascade\s*(?P<Cascade>\d+):\s+'
        'Group\s*(?P<Group>\d+)\s+'
        'Number\s*(?P<Number>\d+)')

    def match(self, strippedline):
        m = self.strippedtitle_re.match(strippedline)
        if m:
            # initialize parseed object
            self.mobj = {'Index': {'Cascade': int(m.group('Cascade')),
                                   'Group': int(m.group('Group')),
                                   'Number': int(m.group('Number'))}}
        else:
            self.mobj = None
        return self.mobj

    def parse(self, einput, mobj=None):
        # mobj is not used
        # self.mobj is updated
        ParserChain.parse(self, einput)

        # test number of records
        assert(len(self.mobj['Cascade Detail']['records']) ==
               len(self.mobj['Cascade2']['records']))
        assert(len(self.mobj['Cascade Detail']['records']) ==
               len(self.mobj['Cascade3']['records']))
        assert(len(self.mobj['Separations of Distant I-V Pairs']['records']) ==
               self.mobj['Summary of Cascade']['Pairs identified'])

        # merge Cascade1, 2, and 3
        for a, b, c in zip(self.mobj['Cascade Detail']['records'],
                           self.mobj['Cascade2']['records'],
                           self.mobj['Cascade3']['records']):
            assert(a['File'] == b['File'])
            assert(a['Karma'] == b['Karma'])
            assert(a['Atom'] == b['Atom'])
            assert(a['File'] == c['File'])
            assert(a['Karma'] == c['Karma'])
            assert(a['Atom'] == c['Atom'])
            a.update(b)
            a.update(c)

        del self.mobj['Cascade2']
        del self.mobj['Cascade3']

        return self.mobj

# csv data formatter

# headers required for cascade data
cascade_idx_headers = ['Cascade', 'Group', 'Number']

# Detailed Description of the Cascade 1, 2, 3
description_of_cascade_headers = cascade_idx_headers + [
    # detail of cascade 1
    'File', 'Atom', 'Karma', 'Initial Time', 'Initial Energy', 'Initial Location X',
    'Initial Location Y', 'Initial Location Z', 'Initial Location Site', 'Trak',
    'Nseq',
    # detail of cascade 2
    'Final Time', 'Final Energy', 'Final Direction Cosine X',
    'Final Direction Cosine Y', 'Final Direction Cosine Z',
    # detail of cascade 3
    'Final Location X', 'Final Location Y', 'Final Location Z',
    'Reference Lattice Site X', 'Reference Lattice Site Y',
    'Reference Lattice Site Z', 'Reference Lattice Site']


def description_of_cascade_rowdata(mobj, rec):
    """Generate list of 'Cascade Detail' record data, which is output in csv format

    mobj is parsed object given by Parser.parse()
    rec is record data in mobj['Cascade Detail']['records']
    """
    return [mobj['Index']['Cascade'], mobj['Index']['Group'], mobj['Index']['Number']] \
        + [rec[k] for k in description_of_cascade_headers[3:]]

# Location of Lattice Sites
lattice_sites_headers = cascade_idx_headers + [
    # lattice sites table data
    'File', 'Lattice Site', 'Lattice Location X', 'Lattice Location Y',
    'Lattice Location Z', 'Paired Atom File',
    # reference to cascade data
    'Paired Atom', 'Paired Atom Final Location X', 'Paired Atom Final Location Y',
    'Paired Atom Final Location Z', 'Distance']


def lattice_sites_rowdata(mobj, rec):
    """Generate list of 'Lattice Sites' record data, which is output in csv format

    mobj is parsed object given by Parser.parse()
    rec is record data in mobj['Lattice Sites']['records']
    """
    rowdata = [mobj['Index']['Cascade'], mobj['Index']['Group'], mobj['Index']['Number']]
    rowdata += [rec['File'], rec['Site'], rec['Location X'], rec['Location Y'],
                rec['Location Z'], rec['Paired Atom File']]
    extrowdata = []
    if 'Cascade Detail' in mobj:
        atomfile = rec['Paired Atom File']
        if atomfile >= 1:
            cascdata = mobj['Cascade Detail']['records'][atomfile-1]
            # calculate distance
            distance = math.sqrt(
                (rec['Location X'] - cascdata['Final Location X'])**2
                + (rec['Location Y'] - cascdata['Final Location Y'])**2
                + (rec['Location Z'] - cascdata['Final Location Z'])**2)

            extrowdata.extend([cascdata['Atom'], cascdata['Final Location X'],
                               cascdata['Final Location Y'], cascdata['Final Location Z'],
                               distance])
    # extrowdata is null replace with [None]*7
    if not extrowdata:
        extrowdata = [None]*7
    rowdata += extrowdata
    return rowdata

# Distant Interstitial Vacancy Pairs
distant_iv_pairs_headers = cascade_idx_headers + [
    # distant I-V table
    'Pair Number', 'Vacancy Site', 'Vacancy File', 'Interstitial Atom',
    'Interstitial File', 'Distance',
    # reference to LatticeSite
    'Vacancy Lattice Location X', 'Vacancy Lattice Location Y',
    'Vacancy Lattice Location Z',
    # reference to cascade data
    'Interstitial Final Location X', 'Interstitial Final Location Y',
    'Interstitial Final Location Z']


def distant_iv_pairs_rowdata(mobj, rec):
    """Generate list of 'Distant I-V pairs' record data, which is output in csv format

    mobj is parsed object given by Parser.parse()
    rec is record data in mobj['Cascade Detail']['records']
    """
    rowdata = [mobj['Index']['Cascade'], mobj['Index']['Group'], mobj['Index']['Number']]
    rowdata += [rec['Pair Number'], rec['Vacancy Site'], rec['Vacancy File'],
                rec['Interstitial Atom'], rec['Interstitial File'], rec['Distance']]
    vacfile = rec['Vacancy File']
    intfile = rec['Interstitial File']

    if 'Lattice Sites' in mobj:
        vacdata = mobj['Lattice Sites']['records'][vacfile-1]
        vacrowdata = [vacdata['Location X'], vacdata['Location Y'], vacdata['Location Z']]
    else:
        vacrowdata = [None]*3

    if 'Cascade Detail' in mobj:
        intdata = mobj['Cascade Detail']['records'][intfile-1]
        introwdata = [intdata['Final Location X'], intdata['Final Location Y'],
                      intdata['Final Location Z']]
    else:
        introwdata = [None]*3

    rowdata += vacrowdata
    rowdata += introwdata

    return rowdata

# Primary Recoil Ranges
primary_recoil_ranges_headers = cascade_idx_headers + \
    ['Elem', 'Radial', 'Penetration', 'Spread', 'Total Path', 'Time (fs)']


def primary_recoil_ranges_rowdata(mobj):
    """Generate list of 'Primary Recoil Ranges' section data, which is output in csv format

    mobj is parsed object given by Parser.parse()
    """
    rowdata = [mobj['Index']['Cascade'], mobj['Index']['Group'], mobj['Index']['Number']]
    d = mobj['Primary Recoil Ranges']
    rowdata += [d['Elem'], d['Radial Range'], d['Penetration'], d['Spread'],
                d['Total Path'], d['Slowing Down Time']]
    return rowdata


# Summary of Cascade
summary_of_cascade_headers = cascade_idx_headers + [
    'Collisions', 'Atoms available for pairing',
    'Sites available for pairing', 'Pairs identified', 'Pair separations > VCR',
    'Unpaired vacant sites', 'Atoms escaping all surfaces',
    'Atoms trapped at all surfaces',
    'Replacement sequences', 'Focuson sequences', 'Truncated trajectories',
    'Beheaded replacement sequences', 'Beheaded focuson sequences',
    'Redisplaced sequence members', 'Other redisplaced targets',
    'Redisplacements, distant pairs', 'Redisplaced adatoms',
    'Multiple redisplacements']


def summary_of_cascade_rowdata(mobj):
    """Generate list of 'Summary of Cascades' section data, which is output in csv format

    mobj is parsed object given by Parser.parse()
    """
    return [mobj['Summary of Cascade'][k] for k in summary_of_cascade_headers]

# Summary of Cascade for each Atom
cascade_summary_each_atom_headers = cascade_idx_headers + \
    ['Elem index', 'Elem'] + \
    ['Num. of '+a for a in cascade_summary_each_atom.number_of_fields] + \
    ['Num. of proper '+a for a in cascade_summary_each_atom.number_of_proper_fields] + \
    ['Num. of improper '+a for a in cascade_summary_each_atom.number_of_improper_fields] + \
    ['Eng. of '+a for a in cascade_summary_each_atom.energy_fields]


def cascade_summary_each_atom_rowdata(mobj, rec):
    """Generate list of 'Cascade Summary for ?? atom' record data, which is output
    in csv format

    mobj is parsed object given by Parser.parse()
    rec is element of mobj['Cascade Summary for each Atom']
    """
    rowdata = [mobj['Index']['Cascade'], mobj['Index']['Group'], mobj['Index']['Number']]
    rowdata += [rec['Index'], rec['Elem']]
    rowdata += [rec['Number of'].get(k, None) for k in
                cascade_summary_each_atom.number_of_fields]
    rowdata += [rec['Number of proper'].get(k, None) for k in
                cascade_summary_each_atom.number_of_proper_fields]
    rowdata += [rec['Number of improper'].get(k, None) for k in
                cascade_summary_each_atom.number_of_improper_fields]
    rowdata += [rec['Energy'].get(k, None) for k in
                cascade_summary_each_atom.energy_fields]
    return rowdata


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
