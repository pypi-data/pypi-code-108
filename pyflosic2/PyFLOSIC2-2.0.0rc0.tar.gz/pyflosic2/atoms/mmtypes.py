from itertools import combinations
import numpy
from pyflosic2 import parameters
from pyflosic2.io.flosic_io import atoms2flosic


class FFLIB:
    """
        FFLIB class
        -----------
        Contains MMtype informations for a force field.
    """

    def __init__(self, name, dct, src):
        self.name = name
        self.dct = dct
        self.src = src


# rappe.csv
uff_rappe = {'Ac6+3': [1.9830000400543213, 90.0, 0.0],
             'Ag1+1': [1.3860000371932983, 180.0, 0.0],
             'Al3': [1.24399995803833, 109.47000122070312, 0.0],
             'Al6': [1.9500000476837158, 90.0, 0.0],
             'Am6+4': [1.659999966621399, 90.0, 0.0],
             'Ar4+4': [1.031999945640564, 90.0, 0.0],
             'As3+3': [1.2109999656677246, 92.0999984741211, 3.0],
             'At': [1.5449999570846558, 180.0, 0.0],
             'Au4+3': [1.2619999647140503, 90.0, 0.0],
             'B_2': [0.828000009059906, 120.0, 3.0],
             'B_3': [0.8379999995231628, 109.47000122070312, 3.0],
             'Ba6+2': [2.2769999504089355, 90.0, 0.0],
             'Be3+2': [1.0740000009536743, 109.47000122070312, 0.0],
             'Bi3+3': [1.5119999647140503, 90.0, 3.0],
             'Bk6+3': [1.7610000371932983, 90.0, 0.0],
             'Br': [1.1920000314712524, 180.0, 0.0],
             'C_1': [0.7059999704360962, 180.0, 0.0],
             'C_2': [0.7319999933242798, 120.0, 3.0],
             'C_3': [0.7570000290870667, 109.47000122070312, 4.0],
             'C_R': [0.7289999723434448, 120.0, 3.0],
             'Ca6+2': [1.7610000371932983, 90.0, 0.0],
             'Cd3+2': [1.402999997138977, 109.0, 0.0],
             'Ce6+3': [1.840999960899353, 90.0, 0.0],
             'Cf6+3': [1.75, 90.0, 0.0],
             'Cl': [1.0440000295639038, 180.0, 0.0],
             'Cm6+3': [1.8009999990463257, 90.0, 0.0],
             'Co6+3': [1.2410000562667847, 90.0, 0.0],
             'Cr6+3': [1.3450000286102295, 90.0, 0.0],
             'Cs': [2.569999933242798, 180.0, 0.0],
             'Cu3+1': [1.3020000457763672, 109.47000122070312, 0.0],
             'Dy6+3': [1.7100000381469727, 90.0, 0.0],
             'Er6+3': [1.6729999780654907, 90.0, 0.0],
             'Es6+3': [1.7239999771118164, 90.0, 0.0],
             'Eu6+3': [1.7710000276565552, 90.0, 0.0],
             'F_': [0.6679999828338623, 180.0, 0.0],
             'Fe3+2': [1.2699999809265137, 109.47000122070312, 0.0],
             'Fe6+2': [1.3350000381469727, 90.0, 0.0],
             'Fm6+3': [1.7120000123977661, 90.0, 0.0],
             'Fr': [2.880000114440918, 180.0, 0.0],
             'Ga3+3': [1.2599999904632568, 109.47000122070312, 0.0],
             'Gd6+3': [1.7350000143051147, 90.0, 0.0],
             'Ge3': [1.1970000267028809, 109.47000122070312, 4.0],
             'H_': [0.3540000021457672, 180.0, 0.0],
             'H_OH': [0.3540000021457672, 180.0, 0.0],
             'H_b': [0.46000000834465027, 83.5, 2.0],
             'He4+4': [0.8489999771118164, 90.0, 0.0],
             'Hf3+4': [1.6109999418258667, 109.47000122070312, 0.0],
             'Hg1+2': [1.340000033378601, 180.0, 0.0],
             'Ho6+3': [1.6959999799728394, 90.0, 0.0],
             'I_': [1.3819999694824219, 180.0, 0.0],
             'In3+3': [1.4589999914169312, 109.47000122070312, 0.0],
             'Ir6+3': [1.371000051498413, 90.0, 0.0],
             'K_': [1.9529999494552612, 180.0, 0.0],
             'Kr4+4': [1.1469999551773071, 90.0, 0.0],
             'La3+3': [1.9429999589920044, 109.47000122070312, 0.0],
             'Li': [1.3359999656677246, 180.0, 0.0],
             'Lu6+3': [1.6710000038146973, 90.0, 0.0],
             'Lw6+3': [1.6979999542236328, 90.0, 0.0],
             'Md6+3': [1.6890000104904175, 90.0, 0.0],
             'Mg3+2': [1.4210000038146973, 109.47000122070312, 0.0],
             'Mn6+2': [1.3819999694824219, 90.0, 0.0],
             'Mo3+6': [1.4839999675750732, 109.47000122070312, 0.0],
             'Mo6+6': [1.4670000076293945, 90.0, 0.0],
             'N_1': [0.656000018119812, 180.0, 0.0],
             'N_2': [0.6850000023841858, 111.19999694824219, 2.0],
             'N_3': [0.699999988079071, 106.69999694824219, 3.0],
             'N_3+4': [0.699999988079071, 106.69999694824219, 4.0],
             'N_R': [0.6990000009536743, 120.0, 3.0],
             'Na': [1.5390000343322754, 180.0, 0.0],
             'Nb3+5': [1.4730000495910645, 109.47000122070312, 0.0],
             'Nd6+3': [1.815999984741211, 90.0, 0.0],
             'Ne4+4': [0.9200000166893005, 90.0, 0.0],
             'Ni4+2': [1.1640000343322754, 90.0, 0.0],
             'No6+3': [1.6790000200271606, 90.0, 0.0],
             'Np6+4': [1.6660000085830688, 90.0, 0.0],
             'O_1': [0.6389999985694885, 180.0, 1.0],
             'O_2': [0.6340000033378601, 120.0, 1.0],
             'O_3': [0.6579999923706055, 104.51000213623047, 2.0],
             'O_3_z': [0.527999997138977, 145.4499969482422, 2.0],
             'O_HH': [0.6579999923706055, 104.51000213623047, 2.0],
             'O_R': [0.6800000071525574, 110.0, 2.0],
             'Os6+6': [1.371999979019165, 90.0, 0.0],
             'P_3+3': [1.1009999513626099, 93.80000305175781, 3.0],
             'P_3+5': [1.055999994277954, 109.47000122070312, 4.0],
             'P_3+q': [1.055999994277954, 109.47000122070312, 4.0],
             'Pa6+4': [1.7109999656677246, 90.0, 0.0],
             'Pb3': [1.4589999914169312, 109.0, 4.0],
             'Pd4+2': [1.3380000591278076, 90.0, 0.0],
             'Pm6+3': [1.8009999990463257, 90.0, 0.0],
             'Po3+2': [1.5, 90.0, 2.0],
             'Pr6+3': [1.8229999542236328, 90.0, 0.0],
             'Pt4+2': [1.3639999628067017, 90.0, 0.0],
             'Pu6+4': [1.656999945640564, 90.0, 0.0],
             'Ra6+2': [2.51200008392334, 90.0, 0.0],
             'Rb': [2.259999990463257, 180.0, 0.0],
             'Re3+7': [1.3140000104904175, 109.47000122070312, 0.0],
             'Re6+5': [1.371999979019165, 90.0, 0.0],
             'Rh6+3': [1.3320000171661377, 90.0, 0.0],
             'Rn4+4': [1.4199999570846558, 90.0, 0.0],
             'Ru6+2': [1.4780000448226929, 90.0, 0.0],
             'S_2': [0.8539999723434448, 120.0, 2.0],
             'S_3+2': [1.0640000104904175, 92.0999984741211, 2.0],
             'S_3+4': [1.0490000247955322, 103.19999694824219, 4.0],
             'S_3+6': [1.0269999504089355, 109.47000122070312, 4.0],
             'S_R': [1.0770000219345093, 92.19999694824219, 2.0],
             'Sb3+3': [1.406999945640564, 91.5999984741211, 3.0],
             'Sc3+3': [1.5130000114440918, 109.47000122070312, 0.0],
             'Se3+2': [1.190000057220459, 90.5999984741211, 2.0],
             'Si3': [1.1169999837875366, 109.47000122070312, 4.0],
             'Sm6+3': [1.7799999713897705, 90.0, 0.0],
             'Sn3': [1.3980000019073486, 109.47000122070312, 4.0],
             'Sr6+2': [2.052000045776367, 90.0, 0.0],
             'Ta3+5': [1.5110000371932983, 109.47000122070312, 0.0],
             'Tb6+3': [1.7319999933242798, 90.0, 0.0],
             'Tc6+5': [1.3220000267028809, 90.0, 0.0],
             'Te3+2': [1.3860000371932983, 90.25, 2.0],
             'Th6+4': [1.7209999561309814, 90.0, 0.0],
             'Ti3+4': [1.4119999408721924, 109.47000122070312, 0.0],
             'Ti6+4': [1.4119999408721924, 90.0, 0.0],
             'Tl3+3': [1.5180000066757202, 120.0, 0.0],
             'Tm6+3': [1.659999966621399, 90.0, 0.0],
             'U_6+4': [1.684000015258789, 90.0, 0.0],
             'V_3+5': [1.4019999504089355, 109.47000122070312, 0.0],
             'W_3+4': [1.5260000228881836, 109.47000122070312, 0.0],
             'W_3+6': [1.3799999952316284, 109.47000122070312, 0.0],
             'W_6+6': [1.3919999599456787, 90.0, 0.0],
             'Xe4+4': [1.2669999599456787, 90.0, 0.0],
             'Y_3+3': [1.6979999542236328, 109.47000122070312, 0.0],
             'Yb6+3': [1.6369999647140503, 90.0, 0.0],
             'Zn3+2': [1.1929999589920044, 109.47000122070312, 0.0],
             'Zr3+4': [1.5640000104904175, 109.47000122070312, 0.0]}

UFFLIB = FFLIB('uff_rappe', uff_rappe, 'https://github.com/DCoupry/autografs/blob/master/autografs/data/uff/rappe.csv')


def symbol2uffsymbol(atom):
    """
        Convert symbol (atoms) to uff-symbols
        -------------------------------------
    """
    sym = atom.symbol
    if len(sym) == 1:
        sym = ''.join([sym, '_'])
    return sym


def get_opt_radius(a, atoms, indices, ufflib):
    """
        Get: optimal radius
        ------------------
        Get optimal radius for atom.
    """
    if len(indices) == 0:
        d1 = 0.7
    else:
        # the average of covalent radii will be used for distances
        others = [symbol2uffsymbol(a) for a in atoms if a.index in indices]
        if len(others) == 0:
            d1 = 0.7
        else:
            d1 = [numpy.mean([v[0] for k, v in ufflib.items()
                              if k.startswith(s)]) for s in others]
            d1 = numpy.mean(d1)
    # get the distances also
    # Note: axis important thx KT
    # d0 = numpy.linalg.norm(atoms[indices].positions-atoms[a].position,axis=1).mean()
    d0 = numpy.linalg.norm(atoms.positions[indices] - atoms[a].position, axis=1).mean()
    dx = d0 - d1
    return dx


def r(r_i, r_j):
    """
        Norm of the position vector
        ---------------------------
    """
    return numpy.linalg.norm(r_i - r_j)


def theta(R_i, R_j, R_k):
    """
        Angle between R_i, R_j, R_k
        ---------------------------
    """
    v1 = (R_j - R_i) / r(R_j, R_i)
    v2 = (R_j - R_k) / r(R_j, R_k)
    dot_product = numpy.dot(v1, v2)
    angle = numpy.arccos(dot_product)
    angle = numpy.degrees(angle)
    return angle


def get_angle(a1, a2, a3):
    """
        Get: Angle (from atoms)
        -----------------------
        Wrapper for theta.
    """
    return theta(a1.position, a2.position, a3.position)


def get_opt_angle(a, atoms, indices):
    """
        Get: optimal angle
        ------------------
        Determine optimal angle for a given atom.

    """
    # linear case
    if len(indices) <= 1:
        da = 180.0
    else:
        angles = numpy.array([get_angle(atoms[a1], atoms[a], atoms[a3]) for a1, a3 in combinations(indices, 2)])
        angles = angles.reshape(-1, 1)
        # find the most resonable angle for this atom
        if angles.shape[0] > 1:
            # round(angles); find unique angles count occrency of unique angles;
            # find all float angles corresponding to the most common angle
            values, counts = numpy.unique(angles.round(0), return_counts=True)
            da = angles[angles.round(0) == values[numpy.argmax(counts)]].mean()
        else:
            da = angles[0, 0]
    return da


def get_opt_type(dx, da, dc, ufflib, types, mincost=1000.):
    """
        Get: optimal MMType
        ------------------
    """
    mintyp = None
    # weights
    w_dx = 1 / 2.50
    w_da = 1 / 180.0
    w_dc = 1 / 4.0
    for typ in types:
        xx, aa, cc = ufflib[typ]
        cost = ((dx - xx)**2) * w_dx
        cost += ((da - aa)**2) * w_da
        cost += ((dc - cc)**2) * w_dc
        if cost < mincost:
            mintyp = typ
            mincost = cost
    return mintyp


def get_mmtypes(p, atoms, bo, fflib=UFFLIB):
    """
        Get: mmtypes for nuclei
        -----------------------
        The general idea/design is inspired by [1].
        The bond order (bo) matrix based on FODs
        replaced the orignal algorithm.
        In addition serveral parts of the original
        algorithms have been redesigned to
        work with minimal depencies (numpy, itertools).
        Also the original ASE dependency have
        beeen completly removed.

        Ref.:
             - [1] AuToGraFS: Automatic Topological Generator for Framework Structures
                   https://pubs.acs.org/doi/abs/10.1021/jp507643v
    """
    p.log.header('MMtype classification')
    fflib = UFFLIB.dct
    p.log.write('fflib: {}'.format(UFFLIB.name))
    # We only need the nuclei
    atoms = atoms2flosic(atoms, sym_fod1=atoms._elec_symbols[0], sym_fod2=atoms._elec_symbols[1])[0]
    bonds = bo
    mmtypes = [None, ] * len(atoms)
    for atom in atoms:
        # get the starting symbol in uff nomenclature
        symbol = symbol2uffsymbol(atom)
        # narrow the choices
        ff_types = [k for k in fflib.keys() if k.startswith(symbol)]
        these_bonds = bonds[atom.index].copy()
        # if only one choice, use it
        if len(ff_types) == 1:
            mmtypes[atom.index] = ff_types[0]
        # aromatics are easy also
        elif (numpy.abs(these_bonds - 1.5) < 1e-6).any():
            ff_types = [typ for typ in ff_types if typ.endswith("R")]
            mmtypes[atom.index] = ff_types[0]
        else:
            indices = numpy.where(these_bonds >= 0.25)[0]
            # coordination
            dc = len(indices)
            # angle
            da = get_opt_angle(atom.index, atoms, indices)
            # radius
            dx = get_opt_radius(atom.index, atoms, indices, fflib)
            # complete data
            mmtypes[atom.index] = get_opt_type(dx, da, dc, fflib, ff_types)
            p.log.write('dr: {:10.5f} da: {:10.5f} dc: {} mmtype: {}'.format(dx, da, dc, mmtypes[atom.index]))
    p.log.write('Bond order matrix (BO):\n {}\nmmtypes: {}'.format(bo, mmtypes))
    return mmtypes


class MMTypes:
    """
        MMTypes class
        -------------
    """

    def __init__(self, p, s, bo):
        self.p = p
        self.s = s
        self.bo = bo

    def _get_mmtypes(self):
        """
            private: get mmtypes call
        """
        return get_mmtypes(self.p, self.s, self.bo)

    def kernel(self):
        """
            Kernel function
            ---------------
        """
        self.mmtypes = self._get_mmtypes()
        return self.mmtypes


if __name__ == '__main__':
    from pyflosic2.systems.uflosic_systems import COH2  # , H2O
    from pyflosic2.atoms.bonds import Bonds
    from pyflosic2.io.flosic_io import write_xyz

    p = parameters()
    s = COH2()  # H2O()
    write_xyz(s, 'system.xyz')
    # calculate bonds
    b = Bonds(p, s)
    b.kernel(eps_val=1.8, eps_cor=1 / 3.)
    bo = b.bo
    print(b.b1)
    # calculate mmtypes
    mm = MMTypes(p, s, bo)
    mm.kernel()
