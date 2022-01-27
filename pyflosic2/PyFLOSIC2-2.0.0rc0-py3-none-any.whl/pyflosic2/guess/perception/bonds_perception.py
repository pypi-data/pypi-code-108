import numpy 
from pyflosic2.units.constants import covalent_radii 
from pyflosic2.atoms.bondorder import get_guess_bond_order
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.guess.perception.magic_bonds import MagicBonds
from pyflosic2.guess.perception.aromatic_perception import aromatic_perception
from pyflosic2.guess.perception.params import max_coordination, get_max_valence, eval_bond_order

def get_atomic_coordination(atoms,nn):
    """
        Get atomic coordination (co)
        ----------------------------
        Atomic coordination (co) is the sum of
        connected neighbours.

        Input
        -----
        atoms   : Atoms(), atoms object/instance
        nn      : numpy.array(), next nearest neighours numpy array

    """
    co = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
    return co

def check_overbonding(atoms,bo,verbose=3):
    """
        Check overbonding/ Maximum coordination check
        ----------------------------------------------
        Check if the atomic valence (va)
        is larger then the maximal valence of the species.

        Input
        -----
        atoms   : Atoms(), atoms object/instance
        bo      : numpy.array(), bond order matrix
        verbose : int(), integer for verbosity/ output level

    """
    # Check overbonding
    # atomic valence
    va = numpy.zeros(len(atoms))
    va_max = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        # get current coordination per atom
        va[i] = bo[i, :].sum()
        # max coordination for the current species
        va_max[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # total penalty score (tps)
    tps = (va - va_max).sum()
    # over bonding (ob)
    ob = numpy.multiply(va > va_max,1)
    if verbose > 3:
        print(f'va \n {va}')
        print(f'va_max \n {va_max}')
        print(f'tps \n {tps}')
    return va, va_max,tps,ob


def clean_overbonding(atoms,nn,bo,btype='LEWIS'):
    """
        Clean over-bonding
        ------------------
        If the current coordination number/ atomic valence (va) 
        is larger then the maximal valence of the species, 
        the bond order (bo) needs to be reduced. 

        (1) Check overbonding 
        (2) Reduce bond order
        (3) Check overbonding 
            repeat (2),(3) until va == va_max 

        Refs 
            - [1] https://onlinelibrary.wiley.com/doi/epdf/10.1002/jcc.24309?saml_referrer
                  Journal of Computational Chemistry 2016, 37, 1191–1205 1193
        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        nn      : numpy.array(), next nearest neighours numpy array 
        bo      : numpy.array(), bond order matrix 
        btype   : str(), bond type, e.g., 'LEWIS' or 'LDQ' 
                  adjust if in case of 'LEWIS' 1e is removed 
                  or in case of 'LDQ' only 0.5e is removed 
                  sets the del_e variable 

        TODO 
            - need to implement H BO for 2 H-B bonds equals 2 
    """
    bo = bo.copy()
    m = {'LEWIS' : 1.0, 'LDQ' : 0.5}
    del_e = m[btype]
    # covalent radii for symbols
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    # initial values 
    va, va_max, tps, ob = check_overbonding(atoms,bo)
    for i in range(0, len(atoms)):
        if ob[i] == 1:
            nn_atoms = nn[i].nonzero()[0].tolist()
            r_tmp = numpy.zeros(len(nn_atoms),dtype=float)
            bo_tmp = numpy.zeros(len(nn_atoms),dtype=float)
            while va[i] > va_max[i]:
                for it, j in enumerate(nn_atoms):
                    # Adjust equilibrium references for Al-Al , B-B bonds 
                    # see Ref [1] page 1192 
                    if atoms[i].symbol == 'Al' and atoms[j].symbol == 'Al':
                        eps = -0.2
                    if atoms[i].symbol == 'B' and atoms[j].symbol == 'B':
                        eps = -0.2
                    else:
                        eps = 0
                    r_ij = numpy.linalg.norm(atoms[j].position - atoms[i].position)
                    r_tmp[it] = r_ij/(rc[i] + rc[j]+eps)
                    bo_tmp[it] = bo[i,j]
                if bo[i,nn_atoms[r_tmp.argmin()]] == bo_tmp.max():
                    # delete del_e for the smallest bond 
                    # if bond order is max for this bond 
                    idx = nn_atoms[r_tmp.argmin()]
                    bo[i,idx] -= del_e
                    bo[idx,i] -= del_e
                else:
                    # delete del_e from bond with max bond order 
                    idx = nn_atoms[bo_tmp.argmax()]
                    bo[i,idx] -= del_e
                    
                    bo[idx,i] -= del_e
                # update all values 
                va, va_max, tps, ob = check_overbonding(atoms,bo)
    return va, bo


class BondsPerception:
    """
        BondsPerception class. 
        ----------------------
        Determine next nearest neighbour relations (nn)
        and determine a simple bond order (nn) using 
        this information.
    """
    def __init__(self,atoms,bo_status,btype,verbose):
        """
            __init__ 
            Initialize an instance of the class. 
        """
        self.atoms = atoms 
        self.bo_status = bo_status 
        self.btype = btype 
        self.verbose = verbose 

    def kernel(self): 
        """
            kernel
            ------
            Main function for this class. 
        """
        # 1.a and 1.b (simple) 
        self.nn, self.bo = get_guess_bond_order(self.atoms)
        self.co = get_atomic_coordination(self.atoms,self.nn)
        self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,self.btype)
        # 1.c Check if bo is optimal (tps value)
        self.tps = eval_bond_order(self.atoms,self.nn,self.bo,verbose=self.verbose)
        # 1.d == 3.c pre check aromaticity 
        # Aromatic rings (5,6 rings)
        # magicbonds may only work for non-aromatic systems currently. 
        self.mmtypes = numpy.zeros(len(self.atoms),dtype=object)
        self.aromatic, self.mmtypes, self.cycles, self.bo = aromatic_perception(self.atoms,self.nn,self.bo,self.mmtypes,btype=self.btype)
        print(self.aromatic,self.bo)
        # If we adjust the bo we need to recalculate va.
        # SS: this is redudant and cause errors because we only update va, why?
        self.va, va_max, tps, ob = check_overbonding(self.atoms,self.bo)
        #print(self.va,self.va_max,self.tps,self.ob)
        # DANGERHANS
        #self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,btype=self.btype)

        self.use_magicbonds = bool(self.aromatic.sum() == 0)
        # If tps == 0.0 the guess is good 
        if self.tps == 0.0:
            self.bo_status  = 'valid'
        # If tps != 0.0 the guess is not good 
        # If we use btype='LDQ' we get a maybe a wrong tps, 
        # and magicbonds may not work correctly with bo[i] = 1.5. 
        if self.bo_status == 'incorrect' and self.use_magicbonds:
            # 1.b (advanced)
            print(">>>>>>>>>>> Start magic") 
            self.nn, self.bo, self.va, self.bonds = MagicBonds(self.atoms,verbose=self.verbose)
            print(f"pre end bond perception bo={self.bo}") 
            self.tps = eval_bond_order(self.atoms,self.nn,self.bo,verbose=self.verbose)
            if self.tps == 0.0:
                self.bo_status = 'valid'
            else:
                self.bo_status =  'undefined'
        print(f"End bond perception, va: {self.va} \n bo: {self.bo}")


