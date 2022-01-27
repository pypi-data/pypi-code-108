import numpy
from pyflosic2 import parameters
from pyflosic2.io.flosic_io import atoms2flosic

# Radii, if not indicated differently
# - [1] https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-4-26#Sec11

ATOM_data = {
    'H': (0.23, 1),
    'He': (0.93, 4),
    'Li': (0.68, 1),
    'Be': (0.35, 4),
    'B': (0.83, 4),
    'C': (0.68, 4),
    'N': (0.68, 4),
    'O': (0.68, 2),
    'F': (0.64, 1),
    'Ne': (1.12, 4),
    'Na': (0.97, 1),
    'Mg': (1.10, 4),
    'Al': (1.35, 4),
    'Si': (1.20, 4),
    'P': (1.05, 4),
    'S': (1.02, 4),
    'Cl': (0.99, 1),
    'Ar': (1.57, 4),
    'K': (1.33, 1),
    'Ca': (0.99, 6),
    'Sc': (1.44, 4),
    'Ti': (1.47, 6),
    'V': (1.33, 4),
    'Cr': (1.35, 6),
    'Mn': (1.35, 6),
    'Fe': (1.34, 6),
    'Co': (1.33, 6),
    'Ni': (1.50, 4),
    'Cu': (1.52, 4),
    'Zn': (1.45, 4),
    'Ga': (1.22, 4),
    'Ge': (1.17, 4),
    'As': (1.21, 4),
    'Se': (1.22, 4),
    'Br': (1.21, 1),
    'Kr': (1.91, 4),
    'Rb': (1.47, 1),
    'Sr': (1.12, 6),
    'Y': (1.78, 4),
    'Zr': (1.56, 4),
    'Nb': (1.48, 4),
    'Mo': (1.47, 6),
    'Tc': (1.35, 6),
    'Ru': (1.40, 6),
    'Rh': (1.45, 6),
    'Pd': (1.50, 4),
    'Ag': (1.59, 2),
    'Cd': (1.69, 4),
    'In': (1.63, 4),
    'Sn': (1.46, 4),
    'Sb': (1.46, 4),  # used the same value as for Sn
    'Te': (1.47, 4),
    'I': (1.40, 1),
    'Xe': (1.98, 4),
    'Cs': (1.67, 1),
    'Ba': (1.34, 6),
    'La': (1.87, 4),
    'Ce': (1.83, 6),
    'Pr': (1.82, 6),
    'Nd': (1.81, 6),
    'Pm': (1.80, 6),
    'Sm': (1.80, 6),
    'Eu': (1.99, 6),
    'Gd': (1.79, 6),
    'Tb': (1.76, 6),
    'Dy': (1.75, 6),
    'Ho': (1.74, 6),
    'Er': (1.73, 6),
    'Tm': (1.72, 6),
    'W': (1.62, 6),  # https://www.webelements.com/tungsten/atom_sizes.html
    'Pt': (1.36, 3),  # https://www.webelements.com/platinum/atom_sizes.html
    'Au': (1.36, 2),  # https://www.webelements.com/gold/atom_sizes.html
    'Hg': (1.32, 1)  # https://www.webelements.com/mercury/atom_sizes.html
}


ATOM_key2idx = {
    'r': 0,
    'max_coord': 1
}


def get_distance(p1, p2):
    """
        Get: distance(p1,p2)
        --------------------
    """
    return numpy.linalg.norm(p2 - p1)


def split_atoms2list(atoms):
    """
        Split Atoms() object in list of particle() objects
        --------------------------------------------------
    """
    return atoms._elements


def core_or_lone(ai, nuclei, eps_cor=1 / 3):
    """
        Check: core or lone FOD
        -----------------------
    """
    # core or lone FOD
    dcut = get_distance(ai.position, nuclei.position)
    if dcut < eps_cor * ATOM_data[nuclei.symbol][ATOM_key2idx['r']]:
        # core FOD
        ai._info = ['core-FOD', nuclei]
    else:
        # lone FOD
        ai._info = ['lone-FOD', nuclei]
    return ai


def bond_count_spin(nuclei, fod, eps_val=1.8, eps_cor=1 / 3.):
    """
        Bond-count per spin (FOD1 or FOD2)
        ----------------------------------
    """
    # Bonder order matrix
    bo = numpy.zeros((len(nuclei), len(nuclei)), dtype=numpy.float64)
    # Lone electrons vector
    lone = numpy.zeros(len(nuclei), dtype=numpy.float64)
    for ai in fod:
        ai._NN = []  # Nearest Neighbor
        ai._info = []  # FOD type info/ classifier
        for p in nuclei:
            r1 = ATOM_data[p.symbol][ATOM_key2idx['r']]
            r1 *= eps_val
            d1 = get_distance(ai.position, p.position)
            # Check if dist(ai-nuc) is smaller then atomic_radius(nuc)*eps
            if d1 < r1:
                ai._NN.append(p.index)
        # If only one NN we have no bond FOD
        # Thus it could only be core or lone FOD
        if len(ai._NN) == 1:
            ai = core_or_lone(ai, nuclei[ai._NN[0]], eps_cor=eps_cor)
            if ai._info[0] == 'lone-FOD':
                lone[ai._NN[0]] += 1
        # Loop over all NN per ai
        # to determine which NNs belong together
        for i in ai._NN:
            for j in ai._NN:
                if i < j:
                    d2 = get_distance(nuclei[i].position, nuclei[j].position)
                    d3 = get_distance(ai.position, nuclei[i].position)
                    d4 = get_distance(ai.position, nuclei[j].position)
                    if d3 < d2 and d4 < d2:
                        # Bond FOD
                        nuclei[i]._bond_count += 1 / 2
                        nuclei[j]._bond_count += 1 / 2
                        key = f'{nuclei[i].index}-{nuclei[j].index}'
                        b = {key: 1 / 2}
                        if key in nuclei[i]._info:
                            nuclei[i]._info[key] = nuclei[i]._info[key] + 1 / 2
                        else:
                            nuclei[i]._info.update(b)
                        if key in nuclei[j]._info:
                            nuclei[j]._info[key] = nuclei[j]._info[key] + 1 / 2
                        else:
                            nuclei[j]._info.update(b)
                        ai._info = ['bond-FOD', nuclei[i], nuclei[j]]
                        bo[i, j] += + 1 / 2
                        bo[j, i] += + 1 / 2
                    # Core or lone FOD
                    if bool(d3 < d2) and not bool(d4 < d2):
                        ai = core_or_lone(ai, nuclei[i], eps_cor=eps_cor)
                        if ai._info[0] == 'lone-FOD':
                            lone[ai._NN[0]] += 1

                    if not bool(d3 < d2) and bool(d4 < d2):
                        ai = core_or_lone(ai, nuclei[j], eps_cor=eps_cor)
                        if ai._info[0] == 'lone-FOD':
                            lone[ai._NN[0]] += 1

    return nuclei, fod, bo, lone


def summary_bonds(p, nuclei, fod1, fod2, bo, lone, eps_val=1.8, eps_cor=1 / 3.):
    """
        Summary: determined bond properties
        -----------------------------------
    """
    # unrestricted case
    info = {}
    p.log.write('eps_val: {} eps_cor: {}'.format(eps_val, eps_cor))
    if fod1 is not None and fod2 is not None:
        p.log.write('Bond order matrix')
        p.log.write(str(bo))
        for n in nuclei:
            p.log.write('symbol: {} index: {} bond-count: {}'.format(n.symbol, n.index, n._bond_count))
            tmp_info = n._info
            info.update(tmp_info)
        p.log.write('Bond order: {}'.format(info))
        p.log.write('Lone: {}'.format(lone))
        for ai in fod1:
            p.log.write(str(ai._info))
        for ai in fod2:
            p.log.write(str(ai._info))
    # restricted case
    if fod1 is not None and fod2 is None:
        bo = bo * 2
        p.log.write('Bond order matrix')
        p.log.write(str(bo))
        for n in nuclei:
            p.log.write('symbol: {} index: {} bond-count: {}'.format(n.symbol, n.index, n._bond_count * 2))
            tmp_info = n._info
            info.update(tmp_info)
        info.update((k, v * 2) for k, v in info.items())
        lone *= 2
        p.log.write('Bond order: {}'.format(info))
        p.log.write('Lone: {}'.format(lone))
        for ai in fod1:
            p.log.write(str(ai._info))
    return info, bo, lone


def analyze_fods(p, nuclei, fod1, fod2, bo, lone, eps_val=1.8, eps_cor=1 / 3.):
    """
        Analyze: which FODs belong to which atom
        ----------------------------------------
        Generate information which can be used
        by the bond2fodmc(bond) function
        to generate fodMC FOD guesses.

        Output
        ------
        b1 : dct(str(): int()), bond FOD1
             ith: nuclei.index- jth: nuclei.index : count FOD1s
        b2 : dct(str(): int()), bond FOD2
             ith: nuclei.index- jth: nuclei.index : count FOD2s

    """
    b1 = {}
    b2 = {}
    l1 = {}
    l2 = {}
    # needed for both (unrestricted, restricted)
    if fod1 is not None:
        b1 = {}
        l1 = {}
        for ai in fod1:
            if ai._info[0] == 'bond-FOD':
                key = f'{ai._info[1].index}-{ai._info[2].index}'
                if key in b1:
                    b1[key] = b1[key] + 1
                else:
                    b1.update({key: 1})
            if ai._info[0] == 'lone-FOD':
                key = f'{ai._info[1].index}'
                if key in l1:
                    l1[key] = l1[key] + 1
                else:
                    l1.update({key: 1})

    # unrestricted case
    if fod1 is not None and fod2 is not None:
        b2 = {}
        l2 = {}
        for ai in fod2:
            if ai._info[0] == 'bond-FOD':
                key = f'{ai._info[1].index}-{ai._info[2].index}'
                if key in b2:
                    b2[key] = b2[key] + 1
                else:
                    b2.update({key: 1})
            if ai._info[0] == 'lone-FOD':
                key = f'{ai._info[1].index}'
                if key in l2:
                    l2[key] = l2[key] + 1
                else:
                    l2.update({key: 1})

    # restricted case
    if fod1 is not None and fod2 is None:
        b2 = b1
        l2 = l1

    return b1, b2, l1, l2


def bond_count(atoms, eps_val=1.8, eps_cor=1 / 3.):
    """
        Bount count for Atoms object
        ----------------------------

        Input
        -----
        eps_val: float(), scaling parameter for valence criterion
        eps_cor: float(), scaling parameter for core cirterion
    """
    [nuclei, fod1, fod2] = atoms2flosic(atoms, sym_fod1=atoms._elec_symbols[0], sym_fod2=atoms._elec_symbols[1])
    bo = None
    lone = None
    if fod1 is not None:
        nuclei = split_atoms2list(nuclei)
        fod1 = split_atoms2list(fod1)

        nuclei, fod1, bo1, lone1 = bond_count_spin(nuclei, fod=fod1, eps_val=eps_val, eps_cor=eps_cor)
        bo = bo1
        lone = lone1
        if fod2 is not None:
            fod2 = split_atoms2list(fod2)
            nuclei, fod2, bo2, lone2 = bond_count_spin(nuclei, fod=fod2, eps_val=eps_val, eps_cor=eps_cor)
            bo += bo2
            lone += lone2
    return nuclei, fod1, fod2, bo, lone


class Bonds():
    """
        Bonds class
        -----------
        Allows to determine bond properties.

    """

    def __init__(self, p, atoms):
        self.p = p
        self.atoms = atoms

    def _bond_count(self):
        """
            Bond-count
            ----------
        """
        self.nuclei, self.fod1, self.fod2, self.bo, self.lone = bond_count(self.atoms,
                                                                           eps_val=self.eps_val,
                                                                           eps_cor=self.eps_cor)

    def _summary_bonds(self):
        """
            Summary: bonds
            --------------
        """
        # Analyze: Which FOD belongs to which atom?
        # - generate spin resolved fodMC information
        self.b1, self.b2, self.l1, self.l2 = analyze_fods(self.p,
                                                          self.nuclei,
                                                          self.fod1,
                                                          self.fod2,
                                                          self.bo,
                                                          self.lone,
                                                          self.eps_val,
                                                          self.eps_cor)

        # Summary: Bond order
        # - Note: for restricted the bond order *2
        self.bond, self.bo, self.lone = summary_bonds(self.p,
                                                      self.nuclei,
                                                      self.fod1,
                                                      self.fod2,
                                                      self.bo,
                                                      self.lone,
                                                      eps_val=self.eps_val,
                                                      eps_cor=self.eps_cor)

    def kernel(self, eps_val=1.8, eps_cor=1 / 3.):
        """
            Kernel function
            ---------------

            Input
            -----
            eps_val: float(), scaling parameter for valence criterion
            eps_cor: float(), scaling parameter for core cirterion

        """
        self.eps_val = eps_val
        self.eps_cor = eps_cor
        self._bond_count()
        self._summary_bonds()


if __name__ == '__main__':
    def test_unrestricted():
        from pyflosic2.systems.uflosic_systems import C6H6
        p = parameters(log_name='UBONDS.log')
        atoms = C6H6()
        b = Bonds(p, atoms)
        b.kernel(eps_val=1.8, eps_cor=1 / 3.)

    def test_restricted():
        from pyflosic2.systems.rflosic_systems import COH2
        p = parameters(log_name='RBONDS.log')
        atoms = COH2()
        b = Bonds(p, atoms)
        b.kernel(eps_val=1.8, eps_cor=1 / 3.)

    test_unrestricted()
    test_restricted()
