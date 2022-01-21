'''common rule, terminal and Transformer using lark'''

import lark

import logging

from ..physics import element

logger = logging.getLogger(__name__)

grammar = '''\
// utilities
int_multiline_array10: _int_multiline_array10_part | (_int_multiline_array10_full+ _int_multiline_array10_part?)
    _int_multiline_array10_part: pint (_S pint)~0..8 _NL
    _int_multiline_array10_full: pint (_S pint)~9 _NL
int_multiline_array15: _int_multiline_array15_part | (_int_multiline_array15_full+ _int_multiline_array15_part?)
    _int_multiline_array15_part: pint (_S pint)~0..13 _NL
    _int_multiline_array15_full: pint (_S pint)~14 _NL
int_multiline_array20:  _int_multiline_array20_part | (_int_multiline_array20_full+ _int_multiline_array20_part?)
    _int_multiline_array20_part: pint (_S pint)~0..18 _NL
    _int_multiline_array20_full: pint (_S pint)~19 _NL

EOF: "$EOF"
%import common.NEWLINE -> _NL
%import common.INT
%import common.SIGNED_INT
%import common.SIGNED_FLOAT
_SS: " " // single whitespace
_S: _SS+ // sequence of whitespace
int: _S? SIGNED_INT      -> int // int with left padding
pint: SIGNED_INT -> int // int without padding
float: _S? SIGNED_FLOAT _S? -> float // float with left and right padding
pfloat: SIGNED_FLOAT -> float // float without padding
'''



fixedwidth_int_values = [2, 3, 4, 5, 6]
def gen_fixedwidth_int_grammar(width):
    return f'''FWINT{width:d}: /([+-]\\d{{{width-1:d}}})|(\\d{{{width:d}}})|(\\*{{{width:d}}})/
    fwint{width:d}: (_S SIGNED_INT) | FWINT{width:d} -> fwint{width:d}'''

grammar_fixedwidth_int = '\n'.join([gen_fixedwidth_int_grammar(i) for i in fixedwidth_int_values])

grammar_ttls_momx = '''\
// general/titles.mfs TTLS0120
TTLS_MOMX_1: "Mean"
TTLS_MOMX_2: "Variance"
TTLS_MOMX_3: "Skewness"
TTLS_MOMX_4: "Kurtosis"
TTLS_MOMX_5: "Std Dev"
TTLS_MOMX_6: "Error"
TTLS_MOMX: TTLS_MOMX_1 _S TTLS_MOMX_2 _S TTLS_MOMX_3 _S TTLS_MOMX_4 _S TTLS_MOMX_5 _S TTLS_MOMX_6
'''

grammar_ttls_label = '''\
// general/titles.mfs TTLS0140
TTLS_LABEL:\
    TTLS_LABEL_1 | TTLS_LABEL_2 | TTLS_LABEL_3 | TTLS_LABEL_4 |\
    TTLS_LABEL_5 | TTLS_LABEL_6 | TTLS_LABEL_7 | TTLS_LABEL_8

TTLS_LABEL_1TO4: TTLS_LABEL_1 | TTLS_LABEL_2 | TTLS_LABEL_3 | TTLS_LABEL_4
TTLS_LABEL_1: "Lattice (collisions)"
TTLS_LABEL_2: "Cascade (collisions)"
TTLS_LABEL_3: "Lattice (deferred)"
TTLS_LABEL_4: "Cascade (deferred)"
TTLS_LABEL_5: "Negative time values"
TTLS_LABEL_6: "Lattice targets"
TTLS_LABEL_7: "Nonlattice targets"
TTLS_LABEL_8: "Vacant lattice sites"

'''

grammar_ttls_dname = '''\
TTLS_DNAME:\
    TTLS_DNAME_1 | TTLS_DNAME_2 | TTLS_DNAME_3 | TTLS_DNAME_4 | TTLS_DNAME_5
    | TTLS_DNAME_6 | TTLS_DNAME_7 | TTLS_DNAME_8 | TTLS_DNAME_9 | TTLS_DNAME_10
    | TTLS_DNAME_11
TTLS_DNAME_1:  "Vacant Sites"
TTLS_DNAME_2:  "Interstitials"
TTLS_DNAME_3:  "Substitutions"
TTLS_DNAME_4:  "Adatoms"
TTLS_DNAME_5:  "Lattice Atoms"
TTLS_DNAME_6:  "Disordered Sites"
TTLS_DNAME_7:  "Lattice Impurities"
TTLS_DNAME_8:  "Nonlattice Atoms"
TTLS_DNAME_9:  "Cascade Vacancies"
TTLS_DNAME_10: "Random Vacancies"
TTLS_DNAME_11: "Empty Sublattice"
'''


grammar_ttls_ename = '''\
TTLS_ENAME:\
    TTLS_ENAME_1 | TTLS_ENAME_2 | TTLS_ENAME_3 | TTLS_ENAME_4 | TTLS_ENAME_5
    | TTLS_ENAME_6 | TTLS_ENAME_7 | TTLS_ENAME_8 | TTLS_ENAME_9 | TTLS_ENAME_10
    | TTLS_ENAME_11 | TTLS_ENAME_12 | TTLS_ENAME_13 | TTLS_ENAME_14 | TTLS_ENAME_15
    | TTLS_ENAME_16 | TTLS_ENAME_17

TTLS_ENAME_1:  "atoms: initial inverse energy distribution"
TTLS_ENAME_2:  "redisplaced atoms: initial inverse energy distribution"
TTLS_ENAME_3:  "redisplaced front adatoms: init inverse energy distribution"
TTLS_ENAME_4:  "redisplaced back adatoms: init inverse energy distribution"
TTLS_ENAME_5:  "other redisplaced adatoms: init inverse energy distribution"
TTLS_ENAME_6:  "atoms escaping the front surface: final inverse energy"
TTLS_ENAME_7:  "atoms escaping the back surface: final inverse energy"
TTLS_ENAME_8:  "atoms escaping the side surfaces: final inverse energy"
TTLS_ENAME_9:  "atoms escaping the other surfaces: final inverse energy"
TTLS_ENAME_10: "atoms causing redisplacements: inverse kinetic energy"
TTLS_ENAME_11: "atoms redisplacing front adatoms: inverse kinetic energy"
TTLS_ENAME_12: "atoms redisplacing back adatoms: inverse kinetic energy"
TTLS_ENAME_13: "atoms redisplacing other adatoms: inverse kinetic energy"
TTLS_ENAME_14: "atoms in subthreshold nonlattice encounters: inverse energy"
TTLS_ENAME_15: "atoms in subthresh front adatom encounters: inverse energy"
TTLS_ENAME_16: "atoms in subthresh back adatom encounters: inverse energy"
TTLS_ENAME_17: "atoms in other subthresh adatom encounters: inverse energy"
'''

grammar_ttls_fname = '''\
TTLS_FNAME:\
    TTLS_FNAME_1 | TTLS_FNAME_2 | TTLS_FNAME_3 | TTLS_FNAME_4 | TTLS_FNAME_5
    | TTLS_FNAME_6 | TTLS_FNAME_7 | TTLS_FNAME_8

TTLS_FNAME_1:  "atoms: final kinetic energy distribution"
TTLS_FNAME_2:  "lattice atoms: subthreshold energy distribution"
TTLS_FNAME_3:  "atoms: paused atom intermediate energy distribution"
TTLS_FNAME_4:  "nonlattice atoms: subthreshold energy distribution"
TTLS_FNAME_5:  "atoms: energy carried by suppressed focusons"
TTLS_FNAME_6:  "front adatoms: final energy distribution"
TTLS_FNAME_7:  "back adatoms: final energy distribution"
TTLS_FNAME_8:  "other adatoms: final energy distribution"
TTLS_FNAME_9:  "front adatoms: subthreshold energy distribution"
TTLS_FNAME_10: "back adatoms: subthreshold energy distribution"
TTLS_FNAME_11: "other adatoms: subthreshold energy distribution"
TTLS_FNAME_12: "front adatoms: paused atom intermediate energy distribution"
TTLS_FNAME_13: "back adatoms: paused atom intermediate energy distribution"
TTLS_FNAME_14: "other adatoms: paused atom intermediate energy distribution"
'''

grammar_ttls_gname = '''\
TTLS_GNAME: TTLS_GNAME_1 | TTLS_GNAME_2

TTLS_GNAME_1:\
    TTLS_GNAME_1_1 | TTLS_GNAME_1_2 | TTLS_GNAME_1_3 | TTLS_GNAME_1_4 | TTLS_GNAME_1_5
    | TTLS_GNAME_1_6 | TTLS_GNAME_1_7 | TTLS_GNAME_1_8 | TTLS_GNAME_1_9 | TTLS_GNAME_1_10
    | TTLS_GNAME_1_11 | TTLS_GNAME_1_12 | TTLS_GNAME_1_13 | TTLS_GNAME_1_14 | TTLS_GNAME_1_15
    | TTLS_GNAME_1_16 | TTLS_GNAME_1_17 | TTLS_GNAME_1_18 | TTLS_GNAME_1_19 | TTLS_GNAME_1_20
    | TTLS_GNAME_1_21 | TTLS_GNAME_1_22
TTLS_GNAME_1_1:  "Inelastic energy loss"
TTLS_GNAME_1_2:  "Binding loss (displacements)"
TTLS_GNAME_1_3:  "Binding loss (replacements)"
TTLS_GNAME_1_4:  "Binding loss (nonlattice)"
TTLS_GNAME_1_5:  "Subthreshold loss (lattice)"
TTLS_GNAME_1_6:  "Paused atom intermediate loss"
TTLS_GNAME_1_7:  "Subthreshold loss (nonlattice)"
TTLS_GNAME_1_8:  "Carried by suppressed focusons"
TTLS_GNAME_1_9:  "Remaining kinetic energy"
TTLS_GNAME_1_10: "Available for damage"
TTLS_GNAME_1_11: "In replacement sequences"
TTLS_GNAME_1_12: "Carried by focusons"
TTLS_GNAME_1_13: "Carried by redisplacements"
TTLS_GNAME_1_14: "Replacement threshold"
TTLS_GNAME_1_15: "Focuson threshold"
TTLS_GNAME_1_16: "Redisplacement threshold"
TTLS_GNAME_1_17: "Of forcibly terminated atoms"
TTLS_GNAME_1_18: "Of atoms cut off in SINGLE"
TTLS_GNAME_1_19: "Carried by truncated focusons"
TTLS_GNAME_1_20: "Cut off replacement sequences"
TTLS_GNAME_1_21: "Carried by truncated stenons"
TTLS_GNAME_1_22: "Carried by lost projectiles"

TTLS_GNAME_2:\
    TTLS_GNAME_2_1 | TTLS_GNAME_2_2 | TTLS_GNAME_2_3 | TTLS_GNAME_2_4 | TTLS_GNAME_2_5
    | TTLS_GNAME_2_6 | TTLS_GNAME_2_7 | TTLS_GNAME_2_8 | TTLS_GNAME_2_9 | TTLS_GNAME_2_10
    | TTLS_GNAME_2_11 | TTLS_GNAME_2_12 | TTLS_GNAME_2_13 | TTLS_GNAME_2_14 | TTLS_GNAME_2_15
    | TTLS_GNAME_2_16 | TTLS_GNAME_2_17 | TTLS_GNAME_2_18 | TTLS_GNAME_2_19 | TTLS_GNAME_2_20
    | TTLS_GNAME_2_21 | TTLS_GNAME_2_22
TTLS_GNAME_2_1:  "Carried through front surface"
TTLS_GNAME_2_2:  "Carried through back surface"
TTLS_GNAME_2_3:  "Carried through side surfaces"
TTLS_GNAME_2_4:  "Carried through other surfaces"
TTLS_GNAME_2_5:  "Binding loss (front surface)"
TTLS_GNAME_2_6:  "Binding loss (back surface)"
TTLS_GNAME_2_7:  "Binding loss (other surfaces)"
TTLS_GNAME_2_8:  "Remain kinetic (front adatoms)"
TTLS_GNAME_2_9:  "Remain kinetic (back adatoms)"
TTLS_GNAME_2_10: "Remain kinetic (other adatoms)"
TTLS_GNAME_2_11: "Paused front adatom loss"
TTLS_GNAME_2_12: "Paused back adatom loss"
TTLS_GNAME_2_13: "Other paused adatom loss"
TTLS_GNAME_2_14: "Subthresh loss, front adatoms"
TTLS_GNAME_2_15: "Subthresh loss, back adatoms"
TTLS_GNAME_2_16: "Subthresh loss, other adatoms"
TTLS_GNAME_2_17: "Carried by redis front adatoms"
TTLS_GNAME_2_18: "Carried by redis back adatoms"
TTLS_GNAME_2_19: "Carried by other redis adatoms"
TTLS_GNAME_2_20: "Front adatom redispl thresh"
TTLS_GNAME_2_21: "Back adatom redispl thresh"
TTLS_GNAME_2_22: "Other adatom redispl thresh"
'''

grammar_ttls_hname = '''\
TTLS_HNAME: TTLS_HNAME_1 | TTLS_HNAME_3 | TTLS_HNAME_4 | TTLS_HNAME_5
TTLS_HNAME_1TO4: TTLS_HNAME_1 | TTLS_HNAME_3 | TTLS_HNAME_4
TTLS_HNAME_1: ".....Number of....."
// TTLS_HNAME_2: ".....Number of....."
TTLS_HNAME_3: ".....Number of proper....."
TTLS_HNAME_4: ".....Number of improper....."
TTLS_HNAME_5: ".....Energy (eV)....."
'''

grammar_ttls_kname = '''\
TTLS_KNAME_1:  ".....Total number of....."
TTLS_KNAME_2:  "Collisions"
TTLS_KNAME_3:  "Atoms available for pairing"
TTLS_KNAME_4:  "Sites available for pairing"
TTLS_KNAME_5:  "Pairs identified"
TTLS_KNAME_6:  "Pair separations > VCR"
TTLS_KNAME_7:  "Unpaired vacant sites"
TTLS_KNAME_8:  "Atoms escaping all surfaces"
TTLS_KNAME_9:  "Atoms trapped at all surfaces"
TTLS_KNAME_10: "Replacement sequences"
TTLS_KNAME_11: "Focuson sequences"
TTLS_KNAME_12: "Truncated trajectories"
TTLS_KNAME_13: "Beheaded replacement sequences"
TTLS_KNAME_14: "Beheaded focuson sequences"
TTLS_KNAME_15: "Redisplaced sequence members"
TTLS_KNAME_16: "Other redisplaced targets"
TTLS_KNAME_17: "Redisplacements, distant pairs"
TTLS_KNAME_18: "Redisplaced adatoms"
TTLS_KNAME_19: "Multiple redisplacements"

TTLS_KNAME_2TO19:\
    TTLS_KNAME_2  | TTLS_KNAME_3  | TTLS_KNAME_4  | TTLS_KNAME_5  | TTLS_KNAME_6  |\
    TTLS_KNAME_7  | TTLS_KNAME_8  | TTLS_KNAME_9  | TTLS_KNAME_10 | TTLS_KNAME_11 |\
    TTLS_KNAME_12 | TTLS_KNAME_13 | TTLS_KNAME_14 | TTLS_KNAME_15 | TTLS_KNAME_16 |\
    TTLS_KNAME_17 | TTLS_KNAME_18 | TTLS_KNAME_19
'''

grammar_ttls_nname = '''\
TTLS_NNAME: TTLS_NNAME_1 | TTLS_NNAME_2 | TTLS_NNAME_3

TTLS_NNAME_1:\
    TTLS_NNAME_1_1 | TTLS_NNAME_1_2 | TTLS_NNAME_1_3 | TTLS_NNAME_1_4 | TTLS_NNAME_1_5\
    | TTLS_NNAME_1_6 | TTLS_NNAME_1_7 | TTLS_NNAME_1_8 | TTLS_NNAME_1_9 | TTLS_NNAME_1_10\
    | TTLS_NNAME_1_11 | TTLS_NNAME_1_12 | TTLS_NNAME_1_13 | TTLS_NNAME_1_14 | TTLS_NNAME_1_15\
    | TTLS_NNAME_1_16 | TTLS_NNAME_1_17 | TTLS_NNAME_1_18 | TTLS_NNAME_1_19 | TTLS_NNAME_1_20
    | TTLS_NNAME_1_21 | TTLS_NNAME_1_22 | TTLS_NNAME_1_23
TTLS_NNAME_1_1:  "Atoms involved"
TTLS_NNAME_1_2:  "Collisions"
TTLS_NNAME_1_3:  "Lattice targets encountered"
TTLS_NNAME_1_4:  "Nonlattice targets encountered"
TTLS_NNAME_1_5:  "Vacant sites encountered"
TTLS_NNAME_1_6:  "Lattice subthreshold events"
TTLS_NNAME_1_7:  "Nonlattice subthreshold events"
TTLS_NNAME_1_8:  "Displaced lattice targets"
TTLS_NNAME_1_9:  "Displaced interstitial targets"
TTLS_NNAME_1_10: "Redisplaced targets"
TTLS_NNAME_1_11: "Lattice subthreshold sites"
TTLS_NNAME_1_12: "Nonlattice subthreshold sites"
TTLS_NNAME_1_13: "Focusons"
TTLS_NNAME_1_14: "Replacement sequences"
TTLS_NNAME_1_15: "Unpaired interstitial atoms"
TTLS_NNAME_1_16: "Unpaired vacant sites"
TTLS_NNAME_1_17: "Redisplaced atoms of this kind"
TTLS_NNAME_1_18: "Forcibly terminated atoms"
TTLS_NNAME_1_19: "Atoms cut-off in SINGLE"
TTLS_NNAME_1_20: "Truncated focusons"
TTLS_NNAME_1_21: "Cut-off replacement sequences"
TTLS_NNAME_1_22: "Truncated stenons"
TTLS_NNAME_1_23: "'Lost' projectiles"

TTLS_NNAME_2:\
    TTLS_NNAME_2_1 | TTLS_NNAME_2_2 | TTLS_NNAME_2_3 | TTLS_NNAME_2_4 | TTLS_NNAME_2_5
    | TTLS_NNAME_2_6 | TTLS_NNAME_2_7 | TTLS_NNAME_2_8 | TTLS_NNAME_2_9 | TTLS_NNAME_2_10
    | TTLS_NNAME_2_11 | TTLS_NNAME_2_12 | TTLS_NNAME_2_13 | TTLS_NNAME_2_14 | TTLS_NNAME_2_15
    | TTLS_NNAME_2_16 | TTLS_NNAME_2_17 | TTLS_NNAME_2_18 | TTLS_NNAME_2_19 | TTLS_NNAME_2_20
    | TTLS_NNAME_2_21 | TTLS_NNAME_2_22
TTLS_NNAME_2_1:  "Atoms escaping front surface"
TTLS_NNAME_2_2:  "Atoms escaping back surface"
TTLS_NNAME_2_3:  "Atoms escaping side surfaces"
TTLS_NNAME_2_4:  "Atoms escaping other surfaces"
TTLS_NNAME_2_5:  "Atoms trapped at front surface"
TTLS_NNAME_2_6:  "Atoms trapped at back surface"
TTLS_NNAME_2_7:  "Atoms trapped, other surfaces"
TTLS_NNAME_2_8:  "Front adatoms encountered"
TTLS_NNAME_2_9:  "Back adatoms encountered"
TTLS_NNAME_2_10: "Other adatoms encountered"
TTLS_NNAME_2_11: "Subthresh front adatom events"
TTLS_NNAME_2_12: "Subthresh back adatom events"
TTLS_NNAME_2_13: "Other subthresh adatom events"
TTLS_NNAME_2_14: "Redispl front adatom targets"
TTLS_NNAME_2_15: "Redispl back adatom targets"
TTLS_NNAME_2_16: "Other redispl targets"
TTLS_NNAME_2_17: "Subthresh front adatom sites"
TTLS_NNAME_2_18: "Subthresh back adatom sites"
TTLS_NNAME_2_19: "Other subthresh adatom sites"
TTLS_NNAME_2_20: "Redisplaced front adatoms"
TTLS_NNAME_2_21: "Redisplaced back adatoms"
TTLS_NNAME_2_22: "Other redisplaced adatoms"

TTLS_NNAME_3:\
    TTLS_NNAME_3_1 | TTLS_NNAME_3_2 | TTLS_NNAME_3_3 | TTLS_NNAME_3_4 | TTLS_NNAME_3_5
    | TTLS_NNAME_3_6 | TTLS_NNAME_3_7 | TTLS_NNAME_3_8 | TTLS_NNAME_3_9 | TTLS_NNAME_3_10
    | TTLS_NNAME_3_11 | TTLS_NNAME_3_12 | TTLS_NNAME_3_13 | TTLS_NNAME_3_14 | TTLS_NNAME_3_15
    | TTLS_NNAME_3_16 | TTLS_NNAME_3_17 | TTLS_NNAME_3_18 | TTLS_NNAME_3_19 | TTLS_NNAME_3_20
    | TTLS_NNAME_3_21 | TTLS_NNAME_3_22 | TTLS_NNAME_3_23 | TTLS_NNAME_3_24 | TTLS_NNAME_3_25
TTLS_NNAME_3_1:  "Atoms in focusons"
TTLS_NNAME_3_2:  "Correlated close pairs"
TTLS_NNAME_3_3:  "Correlated near pairs"
TTLS_NNAME_3_4:  "Total correlated annihilations"
TTLS_NNAME_3_5:  "Replacements"
TTLS_NNAME_3_6:  "Uncorrelated close pairs"
TTLS_NNAME_3_7:  "Uncorrelated near pairs"
TTLS_NNAME_3_8:  "Total site changes"
TTLS_NNAME_3_9:  "Correlated distant pairs"
TTLS_NNAME_3_10: "Uncorrelated distant pairs"
TTLS_NNAME_3_11: "Other distant pairs"
TTLS_NNAME_3_12: "Total distant pairs"
TTLS_NNAME_3_13: "Close front surface pairs"
TTLS_NNAME_3_14: "Close back surface pairs"
TTLS_NNAME_3_15: "Other close surface pairs"
TTLS_NNAME_3_16: "Near front surface pairs"
TTLS_NNAME_3_17: "Near back surface pairs"
TTLS_NNAME_3_18: "Other near surface pairs"
TTLS_NNAME_3_19: "Total surface site changes"
TTLS_NNAME_3_20: "Distant front surface pairs"
TTLS_NNAME_3_21: "Distant back surface pairs"
TTLS_NNAME_3_22: "Other distant surface pairs"
TTLS_NNAME_3_23: "Total distant surface pairs"
TTLS_NNAME_3_24: "Redisplacements, distant pairs"
TTLS_NNAME_3_25: "Redisplacements, surface pairs"
'''

grammar_ttls_qname = '''\
TTLS_QNAME:\
    "atoms: spectrum of energy lost to binding (displacements)"
    | "atoms: spectrum of energy lost to binding (replacements)"
'''

grammar_ttls_tname = '''\
TTLS_TNAME:\
    TTLS_TNAME_1 | TTLS_TNAME_2 | TTLS_TNAME_3 | TTLS_TNAME_4 | TTLS_TNAME_5
    | TTLS_TNAME_6 | TTLS_TNAME_7 | TTLS_TNAME_8 | TTLS_TNAME_9 | TTLS_TNAME_10
    | TTLS_TNAME_11 | TTLS_TNAME_12 | TTLS_TNAME_13 | TTLS_TNAME_14 | TTLS_TNAME_15
    | TTLS_TNAME_16 | TTLS_TNAME_17 | TTLS_TNAME_18 | TTLS_TNAME_19 | TTLS_TNAME_20
    | TTLS_TNAME_21 | TTLS_TNAME_22 | TTLS_TNAME_23 | TTLS_TNAME_24 | TTLS_TNAME_25
    | TTLS_TNAME_26

TTLS_TNAME_1:  "displaced atoms: initial time distribution"
TTLS_TNAME_2:  "replaced atoms: initial time distribution"
TTLS_TNAME_3:  "focuson atoms: initial time distribution"
TTLS_TNAME_4:  "distant pairs and unpaired atoms: final time distribution"
TTLS_TNAME_5:  "replacements, uncorrelated close and near pairs: final time"
TTLS_TNAME_6:  "focusons and correlated close and near pairs: final time"
TTLS_TNAME_7:  "atoms escaping the front surface: final time"
TTLS_TNAME_8:  "atoms escaping the back surface: final time"
TTLS_TNAME_9:  "atoms escaping the side surfaces: final time"
TTLS_TNAME_10: "atoms escaping the other surfaces: final time"
TTLS_TNAME_11: "atoms trapped at the front surface: final time"
TTLS_TNAME_12: "atoms trapped at the back surface: final time"
TTLS_TNAME_13: "atoms trapped at a user-defined surface: final time"
TTLS_TNAME_14: "atoms pausing before redisplacement: final time"
TTLS_TNAME_15: "redisplacements: time of occurrence"
TTLS_TNAME_16: "redisplacements: length of delay"
TTLS_TNAME_17: "front adatoms pausing before redisplacement: final time"
TTLS_TNAME_18: "back adatoms pausing before redisplacement: final time"
TTLS_TNAME_19: "other adatoms pausing before redisplacement: final time"
TTLS_TNAME_20: "front adatom redisplacements: time of occurrence"
TTLS_TNAME_21: "back adatom redisplacements: time of occurrence"
TTLS_TNAME_22: "other adatom redisplacements: time of occurrence"
TTLS_TNAME_23: "front adatom redisplacements: length of delay"
TTLS_TNAME_24: "back adatom redisplacements: length of delay"
TTLS_TNAME_25: "other adatom redisplacements: length of delay"
TTLS_TNAME_26: "Time Order of Collisions"
'''

grammar_ttls_zname = '''\
TTLS_ZNAME:\
    TTLS_ZNAME_1 | TTLS_ZNAME_2 | TTLS_ZNAME_3 | TTLS_ZNAME_4 | TTLS_ZNAME_5
    | TTLS_ZNAME_6 | TTLS_ZNAME_7 | TTLS_ZNAME_8

TTLS_ZNAME_1: "atoms sputtered from front surface: reduced energy spectrum"
TTLS_ZNAME_2: "atoms sputtered from back surface: reduced energy spectrum"
TTLS_ZNAME_3: "atoms sputtered from side surfaces: reduced energy spectrum"
TTLS_ZNAME_4: "atoms sputtered from other surface: reduced energy spectrum"
TTLS_ZNAME_5: "atoms sputtered from front surface: energy spectrum"
TTLS_ZNAME_6: "atoms sputtered from back surface: energy spectrum"
TTLS_ZNAME_7: "atoms sputtered from side surfaces: energy spectrum"
TTLS_ZNAME_8: "atoms sputtered from other surface: energy spectrum"
'''

# create ELEM terminal
# terminal elements should be sorted by the length,
# so that the parser can find the longer element name (ex. Si) faster than the shorter one (ex. S)
#
# grammar_elem_wrong = '''\
# ELEM: "H" | "He"
#     | "Li" | "Be" | "B" | "C" | "N" | "O" | "F" | "Ne"
#     | "Na" | "Mg" | "Al" | "Si" | "P" | "S" | "Cl" | "Ar"
#     | "K" | "Ca" | "Sc" | "Ti" | "V" | "Cr" | "Mn" | "Fe" | "Co"
#     | "Ni" | "Cu" | "Zn" | "Ga" | "Ge" | "As" | "Se" | "Br" | "Kr"
#     | "Rb" | "Sr" | "Y" | "Zr" | "Nb" | "Mo" | "Tc" | "Ru" | "Rh"
#     | "Pd" | "Ag" | "Cd" | "In" | "Sn" | "Sb" | "Te" | "I" | "Xe"
#     | "Cs" | "Ba" | "La" | "Ce" | "Pr" | "Nd" | "Pm" | "Sm" | "Eu"
#     | "Gd" | "Tb" | "Dy" | "Ho" | "Er" | "Tm" | "Yb" | "Lu" | "Hf"
#     | "Ta" | "W" | "Re" | "Os" | "Ir" | "Pt" | "Au" | "Hg" | "Tl"
#     | "Pb" | "Bi" | "Po" | "At" | "Rn" | "Fr" | "Ra" | "Ac" | "Th"
#     | "Pa" | "U" | "Np" | "Pu" | "Am" | "Cm" | "Bk" | "Cf" | "Es"
#     | "Fm" | "Md" | "No" | "Lr" | "Rf" | "Db" | "Sg" | "Bh" | "Hs"
#     | "Mt" | "Ds" | "Rg" | "Cn" | "Uut" | "Fl" | "Uup" | "Lv" | "Uus" | "Uuo"
# '''

elem_symbols = list(element.table_bysym.keys())
elem_symbols.remove('None')
grammar_elem = 'ELEM: ' + '|'.join([f'"{a}"' for a in sorted(elem_symbols, key=lambda s: (-len(s), s))])


class Transformer(lark.Transformer):
    def int(self, args):
        return int(args[0])

    def float(self, args):
        return float(args[0])


# add fwint{width} recievers
def gen_fixedwidth_int_reciever(width):
    def func(self, args):
        if args[0] == '*'*width:
            args[0] = args[0].replace('*', '9')
        return int(args[0])
    return func

for i in fixedwidth_int_values:
    setattr(Transformer, f'fwint{i:d}', gen_fixedwidth_int_reciever(i))
