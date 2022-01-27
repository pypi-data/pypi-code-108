import numpy as np

symbol2number = {'Ac': 89,
                 'Ag': 47,
                 'Al': 13,
                 'Am': 95,
                 'Ar': 18,
                 'As': 33,
                 'At': 85,
                 'Au': 79,
                 'B': 5,
                 'Ba': 56,
                 'Be': 4,
                 'Bh': 107,
                 'Bi': 83,
                 'Bk': 97,
                 'Br': 35,
                 'C': 6,
                 'Ca': 20,
                 'Cd': 48,
                 'Ce': 58,
                 'Cf': 98,
                 'Cl': 17,
                 'Cm': 96,
                 'Cn': 112,
                 'Co': 27,
                 'Cr': 24,
                 'Cs': 55,
                 'Cu': 29,
                 'Db': 105,
                 'Ds': 110,
                 'Dy': 66,
                 'Er': 68,
                 'Es': 99,
                 'Eu': 63,
                 'F': 9,
                 'Fe': 26,
                 'Fl': 114,
                 'Fm': 100,
                 'Fr': 87,
                 'Ga': 31,
                 'Gd': 64,
                 'Ge': 32,
                 'H': 1,
                 'He': 2,
                 'Hf': 72,
                 'Hg': 80,
                 'Ho': 67,
                 'Hs': 108,
                 'I': 53,
                 'In': 49,
                 'Ir': 77,
                 'K': 19,
                 'Kr': 36,
                 'La': 57,
                 'Li': 3,
                 'Lr': 103,
                 'Lu': 71,
                 'Lv': 116,
                 'Mc': 115,
                 'Md': 101,
                 'Mg': 12,
                 'Mn': 25,
                 'Mo': 42,
                 'Mt': 109,
                 'N': 7,
                 'Na': 11,
                 'Nb': 41,
                 'Nd': 60,
                 'Ne': 10,
                 'Nh': 113,
                 'Ni': 28,
                 'No': 102,
                 'Np': 93,
                 'O': 8,
                 'Og': 118,
                 'Os': 76,
                 'P': 15,
                 'Pa': 91,
                 'Pb': 82,
                 'Pd': 46,
                 'Pm': 61,
                 'Po': 84,
                 'Pr': 59,
                 'Pt': 78,
                 'Pu': 94,
                 'Ra': 88,
                 'Rb': 37,
                 'Re': 75,
                 'Rf': 104,
                 'Rg': 111,
                 'Rh': 45,
                 'Rn': 86,
                 'Ru': 44,
                 'S': 16,
                 'Sb': 51,
                 'Sc': 21,
                 'Se': 34,
                 'Sg': 106,
                 'Si': 14,
                 'Sm': 62,
                 'Sn': 50,
                 'Sr': 38,
                 'Ta': 73,
                 'Tb': 65,
                 'Tc': 43,
                 'Te': 52,
                 'Th': 90,
                 'Ti': 22,
                 'Tl': 81,
                 'Tm': 69,
                 'Ts': 117,
                 'U': 92,
                 'V': 23,
                 'W': 74,
                 'X': 0,
                 'Xe': 54,
                 'Y': 39,
                 'Yb': 70,
                 'Zn': 30,
                 'Zr': 40}

number2symbol = {v: k for k, v in symbol2number.items()}


class Particle():
    """
        Particle class
        --------------
        Nuclei or electron.
    """
    name = 'Particle'

    def __init__(self, symbol, position, index=None):
        self._symbol = symbol
        self._position = position
        self._force = None
        self._index = index
        self._bond_count = 0
        self._info = {}
        self._NN = 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @position.getter
    def position(self):
        return np.array(self._position)

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, value):
        self._force = value

    @force.getter
    def force(self):
        return self._force

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @symbol.getter
    def symbol(self):
        return self._symbol

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @index.getter
    def index(self):
        return self._index

    def __add__(self, other):
        pos = []
        pos.extend(self.position)
        pos.extend(other.position)
        sym = []
        sym.extend(self.symbol)
        sym.extend(other.symbol)
        atoms = Atoms(symbols=sym, positions=pos)
        return atoms

    def __repr__(self):
        return f'{self.name}({self._symbol},{self._position})'


class Electron(Particle):
    """
        Electron class
        --------------
        Derived from particle.
    """
    name = 'Electron'


class Nuclei(Particle):
    """
        Nuclei class
        ------------
        Derived from particle.
    """
    name = 'Nuclei'


class Atoms():
    """
        PyFLOSIC2: Atoms
        
        | An Atom consists of nuclei as well electrons, i.e., Atom = Nuclei + Electrons.
        | A collection of Atom is Atoms, i.e., Atoms = Sum of Atoms. 

        Parameters
        ----------
     
        symbols: list(str())
            chemical symbols 
        positions: list(list())
            positions 
        spin: float() 
            spin of the system 
        charge: float()
            charge of the system 
        elec_symbols: list(str(),str())
            chemical symbols for alpha and beta electrons

        Examples
        --------

        >>> sym = ['C', 'H', 'H', 'H', 'H', 'X', 'He']
        >>> p0 = [+0.00000000, +0.00000000, +0.00000000]
        >>> p1 = [+0.62912000, +0.62912000, +0.62912000]
        >>> p2 = [-0.62912000, -0.62912000, +0.62912000]
        >>> p3 = [+0.62912000, -0.62912000, -0.62912000]
        >>> p4 = [-0.62912000, +0.62912000, -0.62912000]
        >>> pos = [p0, p1, p2, p3, p4, p0, p0]
        >>> atoms = Atoms(symbols=sym, positions=pos, spin=0, charge=0)
        >>> print(atoms)
        >>> print(atoms.positions)

    """

    def __init__(self, symbols, positions, spin=0, charge=0, elec_symbols=['X', 'He']):
        self._symbols = symbols
        self._positions = positions
        self._forces = None
        self._spin = spin
        self._charge = charge
        # Symbols for alpha/beta electrons
        self._elec_symbols = elec_symbols
        # Initialize generator from particles
        self._gen = zip(enumerate(self._symbols), self._positions)
        # Number of nuclei (Nnuc)
        self._Nnuc = len([s for s in symbols if s not in elec_symbols])
        # Number of electrons (Nele)
        self._Nalpha = len([s for s in symbols if s is elec_symbols[0]])
        self._Nbeta = len([s for s in symbols if s is elec_symbols[1]])
        self._Nele = len(symbols) - self._Nnuc
        self._elements = self._get_elements()

    def _get_elements(self):
        # Gives list of particles
        elements = []
        for s, p in zip(enumerate(self._symbols), self._positions):
            i, s = s
            if s not in self._elec_symbols:
                e = Nuclei(s, p, i)
            else:
                e = Electron(s, p, i)
            elements.append(e)
        return elements

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, value):
        # Update Atoms positions
        self._positions = value
        # Update particle._position
        for i, v in enumerate(value):
            self._elements[i].position = v

    @positions.getter
    def positions(self):
        return np.array(self._positions)

    def get_positions(self):
        return np.array(self._positions)

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        # Update Atoms symbols
        self._symbols = value
        # Update particle._symbol
        for i, v in enumerate(value):
            self._elements[i].symbol = v

    @symbols.getter
    def symbols(self):
        return self._symbols

    def get_chemical_symbols(self):
        return self._symbols

    def get_cf(self):
        sym = sorted(self._symbols)
        cf = ''
        for i in set(sym):
            v = sym.count(i)
            if v != 1:
                cf += '{}{}'.format(i, v)
            else:
                cf += '{}'.format(i)
        return cf

    def __repr__(self):
        # Nuclei + Electrons
        if self._Nnuc != 0 and self._Nele != 0:
            return f'Atoms(nuclei:{self._Nnuc},electrons:{self._Nele},spin:{self._spin},charge:{self._charge})'
        # Nuclei only
        if self._Nnuc != 0 and self._Nele == 0:
            return f'Atoms(nuclei:{self._Nnuc},spin:{self._spin},charge:{self._charge})'
        # Electrons only
        if self._Nnuc == 0 and self._Nele != 0:
            return f"Atoms(electrons:{self._Nele},symbol='{self._symbols[0]}')"

    def __next__(self):
        # Give next particle in self.iter(self._elements)
        return next(self.iter)

    def __iter__(self):
        # Make a iterator of list of particles (self._elements)
        self.iter = iter(self._elements)
        return self.iter

    def __getitem__(self, idx):
        # Single index, e.g., for-loops
        if not isinstance(idx, list):
            return self._elements[idx]
        # Indices as list
        # To preserve state of the particles
        # we copy self._elements to sliced atoms object
        if isinstance(idx, list):
            sym = []
            pos = []
            ele = []
            for i in idx:
                sym.append(self._symbols[i])
                pos.append(self._positions[i])
                ele.append(self._elements[i])
            atoms = Atoms(sym,
                          pos,
                          spin=self._spin,
                          charge=self._charge,
                          elec_symbols=self._elec_symbols)
            atoms._elements = ele
            return atoms

    def __len__(self):
        return len(self._symbols)

    def __add__(self, other):
        pos = []
        pos.extend(self.positions)
        pos.extend(other.positions)
        sym = []
        sym.extend(self.symbols)
        sym.extend(other.symbols)
        atoms = Atoms(symbols=sym,
                      positions=pos,
                      spin=self._spin,
                      charge=self._charge,
                      elec_symbols=self._elec_symbols)
        return atoms

    def copy(self):
        """
           Return a copy.
        """
        atoms = self.__class__(symbols=self._symbols,
                               positions=self._positions,
                               spin=self._spin,
                               charge=self._charge,
                               elec_symbols=self._elec_symbols)
        return atoms


if __name__ == '__main__':
    sym = ['C', 'H', 'H', 'H', 'H', 'X', 'He']
    p0 = [+0.00000000, +0.00000000, +0.00000000]
    p1 = [+0.62912000, +0.62912000, +0.62912000]
    p2 = [-0.62912000, -0.62912000, +0.62912000]
    p3 = [+0.62912000, -0.62912000, -0.62912000]
    p4 = [-0.62912000, +0.62912000, -0.62912000]
    pos = [p0, p1, p2, p3, p4, p0, p0]
    atoms = Atoms(symbols=sym, positions=pos, spin=0, charge=0)
    print(atoms)
    print(atoms.positions)
    for a in range(len(atoms)):
        print(atoms[a])
    for a in atoms:
        print(a)
    e = Electron('X', [1, 0, 0])
    e.symbol = 'Hans'
    print(e.force)
    sym_num = [symbol2number[s] for s in sym]
    print(sym_num)
    from pyflosic2.io.uflosic_io import atoms2pyscf
    print(atoms2pyscf(atoms))
    # print([[atom.symbol, atom.position] for atom in atoms])
    # print([atom for atom in atoms])
    print(atoms + atoms)
    print(atoms[[atom.index for atom in atoms if atom.index < 2]])
    a1 = Nuclei('H', [0, 0, 1])
    e1 = Electron('X', [0, 0, 1])
    print(a1 + e1)
