import numpy 
from pyflosic2.ff.uff_params import UFF_params, UFF_key2idx
from pyflosic2.guess.perception.bonds_perception import get_atomic_coordination, get_max_valence

# What are metals? 
# ----------------
# List containing metals. 
metals = ['Li', 'Be', 'Al', 'Sc', 'Ti', 'V',
            'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'Y', 'Zr', 'Nb', 'Mo',
            'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In',
            'Sn', 'Sb', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho',
            'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
            'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra',
            'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am',
            'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md',
            'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs',
            'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl',
            'Mc', 'Lv', 'Ts', 'Og']

def get_hybridization(atoms,nn,co,va,verbose=3):
    """
        Get hybridization 
        -----------------
        Get lone-pairs and sp - hybridization. 
        Limits: ['H','C','N','O','Si','P','S']

        sp = 1 : sp, linear hybridization 
        sp = 2 : sp2, trigonal hybridization 
        sp = 3 : sp3, tetrahedral hybridization 
    """
    # lone electrons
    l = numpy.zeros(len(atoms))
    # sp hybridization 
    sp = numpy.zeros(len(atoms))
    # atomic coordination 
    co = get_atomic_coordination(atoms,nn)
    for i in range(0, len(atoms)):
        if atoms[i].symbol in ['H','C','N','O','Si','P','S']:
            ve = get_max_valence(atoms[i].symbol,co[i])
            l[i] = (ve - va[i])
            sp[i] = co[i] + numpy.ceil(l[i]/2.) -1
            if verbose > 3:
                print(f'{atoms[i].symbol} co: {co[i]} , va: {va[i]}, ve: {ve}, l: {l[i]} sp: {sp[i]} va + li: {va[i] + l[i]}')
    if verbose > 3:
        print(f'l: {l}')
        print(f'sp: {sp}')
    return l, sp

def clean_hybridization(atoms,nn,sp,verbose=3):
    """
        Clean hybridization
        -------------------
        Apply special rules 
        - for O if any neighbor is sp2 O is sp2 
          otherwise O is sp3 
          Ref.: https://pubs.acs.org/doi/suppl/10.1021/acs.jcim.0c00076/suppl_file/ci0c00076_si_001.pdf
    
    """
    for i in range(0, len(atoms)):
        # Special rules for O 
        if atoms[i].symbol == 'O':
            idx_j = nn[i].nonzero()[0].tolist()
            nn_sp2 = (numpy.array(sp[idx_j]) == 2).any()
            if nn_sp2:
                sp[i] = 2
    return sp

def get_formal_charges(atoms,nn,co,va,l,bo,verbose=3):
    """
        Get formal charges
        ------------------
        Get formal charges for each symbol.

            fc[i]= ve[i] - l[i] - va[i]
    """
    # formal charges
    fc = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        ve = get_max_valence(atoms[i].symbol,co[i])
        fc[i] = ve - (l[i] + va[i])
        if verbose > 3:
            print(f'{atoms[i].symbol} {fc[i]}')
    return fc

def get_charge(ox,fc,verbose=3):
    """
        Get charge
        ----------
        Get charge of the system.
        - Sum of the oxidation numbers
        - Sum of the formal charges
    """
    charge_ox = ox.sum()
    charge_fc = fc.sum()
    if verbose > 3:
        print(f'charge : sum ox_i : {charge_ox} sum fc_i : {charge_fc}')
    return charge_fc

def get_spin(l,verbose=3):
    """
        Get spin
        --------
        Get spin (multiplicity) of the system.

            M = 2S + 1 = spin + 1
            M = unpaired_elec + 1

            spin = N_alpha - N_beta

    """
    # Number of lone electrons
    lone_elec = l.sum()
    # integer devision
    # Number of paired lone electrons
    paired_elec = lone_elec // 2 * 2
    # Number of unpaired lone electrons
    unpaired_elec = lone_elec - paired_elec
    M = unpaired_elec + 1
    if verbose > 3:
        print(f'l = {l}')
        print(f'M = {M}')
    return M


def get_uff_symbol(symbol):
    """
        Get UFF symbol
        --------------
        Get 1st two letters from UFF symbol. 
        (e.g., 'F_' vs. 'Fe')
    """
    if len(symbol) == 1:
        return symbol+'_'
    else:
        return symbol

def get_oxidation_numbers(atoms,nn,bo,verbose=3):
    """
        Get oxidation numbers 
        ---------------------
    """
    ox = numpy.zeros(len(atoms))
    for i in range(len(atoms)):
        for j in nn[i].nonzero()[0].tolist():
            symbols_i = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol))]
            if symbols_i:
                sym_i = symbols_i[0]
            symbols_j = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol))]
            if symbols_j:
                sym_j = symbols_j[0]
            #print(sym_i,sym_j)
            Xi = UFF_params[sym_i][UFF_key2idx['Xi']]
            Xj = UFF_params[sym_j][UFF_key2idx['Xi']]
            if Xj > Xi:
                ox[i] += bo[i,j]
            if Xj < Xi:
                ox[i] -= bo[i,j]
            if Xj == Xi:
                ox[i] += 0
    return ox

def get_geometry_metal(atoms,nn):
    """
        Get geometry type for metals
        ----------------------------
    """
    mtyp_geo = numpy.empty((len(atoms)),dtype=object)
    for i in range(len(atoms)):
        if atoms[i].symbol in metals:
            idx = nn[i].nonzero()[0]
            Nnn = len(idx)
            if Nnn < 4:
                typ_geo = 'tetrahedral'
            if Nnn > 4:
                typ_geo = 'octahedral'
            if Nnn == 4:
                typ_geo = ['tetrahedral','square_planar']
                angles = numpy.array([get_angle(atoms[a1], atoms[i], atoms[a3]) for a1, a3 in combinations(idx, 2)])
                for t in typ_geo:
                    if t == 'tetrahedral':
                        E_t = ((angles - 109.47)**2).sum()
                    if t == 'square_planar':
                        E_sp = numpy.array([(angles - 90)**2,(angles - 180)**2]).min().sum()
                if E_sp < E_t:
                    typ_geo = 'square_planar'
                if E_sp > E_t:
                    typ_geo = 'tetrahedral'
            mtyp_geo[i] = typ_geo
    return mtyp_geo

def get_atomic_perception(atoms,nn,co,sp,ox,verbose=3):
    """
        Get atomic perception 
        ---------------------
        Assign MMTypes (e.g., UFF MMTypes). 
    """
    mmtypes = numpy.zeros(len(atoms),dtype=object)
    for i in range(len(atoms)):
        if atoms[i].symbol == 'H':
            # H assigment 
            # if H is bonded to 2 B it is 'H_b' 
            # otherwise it is 'H_'
            symbols_j = numpy.array([a.symbol for a in atoms[nn[i].nonzero()[0].tolist()]])
            values, counts = numpy.unique(symbols_j,return_counts=True)
            for s,c in zip(values,counts):
                if s == 'B' and c >= 2:
                    mmtypes[i] = 'H_b'
                else:
                    mmtypes[i] = 'H_'
        else:
            symbols_i = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol)) != -1 ]
            for sym in symbols_i:
                if len(sym) == 2:
                    if atoms[i].symbol == sym:
                        mmtypes[i] = sym
                if len(sym) == 3:
                    # sym + sp 
                    if verbose > 3:
                        print(sym[0:2],sym[2])
                        print(sym,sp[i],atoms[i].symbol+'_'+str(int(sp[i])))
                    if atoms[i].symbol+'_'+str(int(sp[i])) == sym:
                        mmtypes[i] = sym
                if len(sym) == 5:
                    # sym + co + ox
                    if verbose > 3:
                        print(sym[0:2],sym[2],sym[3:])
                        print(sym,co[i],ox[i])
    if verbose > 3:
        print(f'mmtypes: {mmtypes}')
    return mmtypes

class AtomsPerception:
    """
        AtomsPerception class
        ---------------------
        Determines the local chemical environment 
        and with that the molecular mechanics datatypes (UFF). 
    """
    def __init__(self,atoms,nn,co,va,bo,verbose=3): 
        """
            __init__
            Initialize an instance of the class.
        """
        self.atoms = atoms 
        self.nn = nn 
        self.co = co 
        self.va = va 
        self.bo = bo 
        self.verbose = verbose 
        
    def kernel(self): 
        """
            kernel 
            ------
            Main function for this class. 

            atoms_perception
            2.a Hybridization and metal center geometries
            2.b Oxidation numbers computation
            2.c Atom types assignment
            2.d Charge and spin computation
        """
        # 2.a
        # hybridization: general
        self.l, self.sp = get_hybridization(self.atoms,self.nn,self.co,self.va)
        # hybridization: special rules
        self.sp = clean_hybridization(self.atoms,self.nn,self.sp,verbose=self.verbose)
        # formal charges
        self.fc = get_formal_charges(self.atoms,self.nn,self.co,self.va,self.l,self.bo,verbose=3)
        # geometries of metals
        self.mtype_geo = get_geometry_metal(self.atoms,self.nn)
        # 2.b
        self.ox = get_oxidation_numbers(self.atoms,self.nn,self.bo,verbose=self.verbose)
        # 2.c
        self.mmtypes = get_atomic_perception(self.atoms,self.nn,self.co,self.sp,self.ox,verbose=self.verbose)
        # 2.d
        # charge of the system
        self.charge = get_charge(self.ox,self.fc,verbose=self.verbose)
        # spin of the system
        self.M = get_spin(self.l,verbose=self.verbose)
    
