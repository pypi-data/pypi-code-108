"""Parse 'Cascade Summary for (Elem) atom' section
shown in cascade/report.mfs:1220
this section consists of
 - HNAME(1) # .....Number of.....
   NNAME(L,1) NUMBER(L,1) L = 1:25
 - HNAME(2) # .....Number of.....
   NNAME(L,2) NUMBER(L,2)
 - HNAME(3) # .....Number of proper.....
   NNAME(L,3) NUMBER(L,3)
 - HNAME(4) # .....Number of improper.....
   NNAME(L,3) NUMBER(L,4)
 - HNAME(5) # .....Energy (eV).....
   GNAME(L,1) ERGON(L, 1) for L=1:22
 - HNAME(5) # .....Energy (eV).....
   GNAME(L,2) ERGON(L, 2) for L=1:22
"""

import re

from . import util
from .abstractparser import AbstractParser, testframe
from .fixedfieldparser import FixedFieldParser

# CHARACTER*30 NNAME()
# single field: (6X,10X,A,I10)
# double field: (6X,10X,A,I10,16X,A,I10)
recordparser_nname_odd = FixedFieldParser([(None, 16, None),
                                           ('key', 30, lambda a: a.strip()),
                                           ('value', 10, int)])
nname_odd_linewidth = 57  # 16+30+10+len('\n')
recordparser_nname_even = FixedFieldParser([(None, 56+16, None),
                                            ('key', 30, lambda a: a.strip()),
                                            ('value', 10, int)])

# CHARACTER*30 GNAME()
# single field: (6X,8X,A,G14.6)
# double field: (6X,8X,A,G14.6,16X,A,G14.6)
recordparser_gname_odd = FixedFieldParser([(None, 14, None),
                                           ('key', 30, lambda a: a.strip()),
                                           ('value', 14, float)])
gname_odd_linewidth = 59  # 16+30+10+len('\n')
recordparser_gname_even = FixedFieldParser([(None, 58+16, None),
                                            ('key', 30, lambda a: a.strip()),
                                            ('value', 14, float)])

nname_1 = [
    'Atoms involved', 'Collisions', 'Lattice targets encountered',
    'Nonlattice targets encountered', 'Vacant sites encountered',
    'Lattice subthreshold events', 'Nonlattice subthreshold events',
    'Displaced lattice targets', 'Displaced interstitial targets',
    'Redisplaced targets', 'Lattice subthreshold sites', 'Nonlattice subthreshold sites',
    'Focusons', 'Replacement sequences', 'Unpaired interstitial atoms',
    'Unpaired vacant sites',
    'Redisplaced atoms of this kind', 'Forcibly terminated atoms',
    'Atoms cut-off in SINGLE', 'Truncated focusons', 'Cut-off replacement sequences',
    'Truncated stenons', "'Lost' projectiles"]

nname_2 = [
    'Atoms escaping front surface', 'Atoms escaping back surface',
    'Atoms escaping side surfaces', 'Atoms escaping other surfaces',
    'Atoms trapped at front surface', 'Atoms trapped at back surface',
    'Atoms trapped, other surfaces', 'Front adatoms encountered',
    'Back adatoms encountered',
    'Other adatoms encountered', 'Subthresh front adatom events',
    'Subthresh back adatom events', 'Other subthresh adatom events',
    'Redispl front adatom targets', 'Redispl back adatom targets',
    'Other redispl targets', 'Subthresh front adatom sites', 'Subthresh back adatom sites',
    'Other subthresh adatom sites', 'Redisplaced front adatoms', 'Redisplaced back adatoms',
    'Other redisplaced adatoms']

number_of_fields = nname_1 + nname_2

nname_3 = [
    'Atoms in focusons', 'Correlated close pairs', 'Correlated near pairs',
    'Total correlated annihilations', 'Replacements', 'Uncorrelated close pairs',
    'Uncorrelated near pairs', 'Total site changes', 'Correlated distant pairs',
    'Uncorrelated distant pairs', 'Other distant pairs', 'Total distant pairs',
    'Close front surface pairs', 'Close back surface pairs', 'Other close surface pairs',
    'Near front surface pairs', 'Near back surface pairs', 'Other near surface pairs',
    'Total surface site changes', 'Distant front surface pairs',
    'Distant back surface pairs',
    'Other distant surface pairs', 'Total distant surface pairs',
    'Redisplacements, distant pairs', 'Redisplacements, surface pairs']

number_of_proper_fields = nname_3
number_of_improper_fields = nname_3

gname_1 = [
    'Inelastic energy loss', 'Binding loss (displacements)',
    'Binding loss (replacements)', 'Binding loss (nonlattice)',
    'Subthreshold loss (lattice)',
    'Paused atom intermediate loss', 'Subthreshold loss (nonlattice)',
    'Carried by suppressed focusons', 'Remaining kinetic energy', 'Available for damage',
    'In replacement sequences', 'Carried by focusons', 'Carried by redisplacements',
    'Replacement threshold', 'Focuson threshold', 'Redisplacement threshold',
    'Of forcibly terminated atoms', 'Of atoms cut off in SINGLE',
    'Carried by truncated focusons', 'Cut off replacement sequences',
    'Carried by truncated stenons', 'Carried by lost projectiles']

gname_2 = [
    'Carried through front surface', 'Carried through back surface',
    'Carried through side surfaces', 'Carried through other surfaces',
    'Binding loss (front surface)', 'Binding loss (back surface)',
    'Binding loss (other surfaces)', 'Remain kinetic (front adatoms)',
    'Remain kinetic (back adatoms)', 'Remain kinetic (other adatoms)',
    'Paused front adatom loss', 'Paused back adatom loss',
    'Other paused adatom loss', 'Subthresh loss, front adatoms',
    'Subthresh loss, back adatoms', 'Subthresh loss, other adatoms',
    'Carried by redis front adatoms', 'Carried by redis back adatoms',
    'Carried by other redis adatoms', 'Front adatom redispl thresh',
    'Back adatom redispl thresh', 'Other adatom redispl thresh']

energy_fields = gname_1 + gname_2


class SubTitleParser(object):
    def __init__(self, key, recordparser_odd, recordparser_even, odd_linewidth, fields):
        self.key = key
        self.recordparser_odd = recordparser_odd
        self.recordparser_even = recordparser_even
        self.odd_linewidth = odd_linewidth
        self.fields = fields

number_of = SubTitleParser('Number of', recordparser_nname_odd, recordparser_nname_even,
                           nname_odd_linewidth, number_of_fields)
number_of_proper = SubTitleParser('Number of proper', recordparser_nname_odd,
                                  recordparser_nname_even, nname_odd_linewidth,
                                  number_of_proper_fields)
number_of_improper = SubTitleParser('Number of improper', recordparser_nname_odd,
                                    recordparser_nname_even, nname_odd_linewidth,
                                    number_of_improper_fields)
energy = SubTitleParser('Energy', recordparser_gname_odd,
                        recordparser_gname_even, gname_odd_linewidth, energy_fields)

# (6X,10X,A,26X,A/) or (6X,10X,A/) for HNAME(1-4)
# (6X,8X,A,30X,A/) for HNAME(5)
stfmt_11 = ' '*16+'{0:30s}\n'
stfmt_12 = ' '*16+'{0:30s}'+' '*26+'{0:30s}\n'
stfmt_51 = ' '*14+'{0:30s}\n'
stfmt_52 = ' '*14+'{0:30s}'+' '*30+'{0:30s}\n'

subtitle_parsers = {
    stfmt_11.format('     .....Number of.....', ''): number_of,
    stfmt_12.format('     .....Number of.....', ''): number_of,
    stfmt_11.format('  .....Number of proper.....', ''): number_of_proper,
    stfmt_12.format('  .....Number of proper.....', ''): number_of_proper,
    stfmt_11.format(' .....Number of improper.....', ''): number_of_improper,
    stfmt_12.format(' .....Number of improper.....', ''): number_of_improper,
    stfmt_51.format('    .....Energy (eV).....', ''): energy,
    stfmt_52.format('    .....Energy (eV).....', ''): energy}


class Parser(AbstractParser):
    strippedtitle_re = re.compile(r'Cascade Summary for (?P<Elem>\w+) atoms')

    def match(self, strippedline):
        m = self.strippedtitle_re.match(strippedline)
        if m:
            return {'Elem': m.group('Elem'),
                    'strippedtitle': strippedline}
        return None

    def parse(self, einput, mobj=None):
        # initialized subtitle fields
        for p in subtitle_parsers.values():
            mobj[p.key] = {}

        subtitle_parser = None

        while True:
            try:
                lineno, line = util.skip_to_nonblankline(einput, False)
            except StopIteration:
                break

            # new page?
            strippedline = line.strip()
            if strippedline == mobj['strippedtitle']:
                # pick up next non-blank line (subtitle line is expected)
                continue

            # subtitle?
            if line in subtitle_parsers:
                subtitle_parser = subtitle_parsers[line]
                continue

            # parse it may raise parse error
            # in such case, hold this line and break the loop
            try:
                # parse odd part
                m = subtitle_parser.recordparser_odd.parse(line)
                mobj[subtitle_parser.key][m['key']] = m['value']
                if len(line) > subtitle_parser.odd_linewidth:
                    # parse even part
                    m = subtitle_parser.recordparser_even.parse(line)
                    mobj[subtitle_parser.key][m['key']] = m['value']
            except:
                # ToDO: better error handling process should be considered
                # print(e, file=sys.stderr)
                einput.hold()
                break
        return mobj


if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
