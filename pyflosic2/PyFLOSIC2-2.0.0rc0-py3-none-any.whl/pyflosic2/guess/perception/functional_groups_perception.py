import numpy
from pyflosic2.guess.perception.aromatic_perception import aromatic_perception
from pyflosic2.guess.perception.magic_bonds import magic_aromatic_perception

def get_is_amide(idx,atoms,nn,bo,mmtypes,rules='UFF'):
    """
        Functional group check: Amide 
        -----------------------------
        if is_amide: 
            bo[C,N] = bo[N,C] = 1.41 
            mmtypes[C] = 'C_R'
            mmtypes[N] = 'N_R'
    """
    is_amide = False
    has_O = False
    idx_O = None
    has_N = False
    idx_N = None

    if atoms[idx].symbol == 'C':
        idx_j = nn[idx].nonzero()[0].tolist()
        for j in idx_j:
            sym_j = atoms[j].symbol
            if 'O' == sym_j:
                has_O = True
                idx_O = j
            if 'N' == sym_j:
                has_N = True
                idx_N = j
            if has_O and has_N:
                is_amide = True
                # Change types to aromatic 
                if rules == 'UFF':
                    mmtypes[idx] = 'C_R'
                    mmtypes[idx_N] = 'N_R'
                if rules == 'openbabel':
                    mmtypes[idx] = 'C_2'
                    mmtypes[idx_N] = 'N_2'
                # Change bond order
                bo[idx,idx_N] = 1.41
                bo[idx_N,idx] = 1.41
    return is_amide, bo,  mmtypes

def get_is_nitro(idx,atoms,nn,bo,mmtypes):
    """
        Functional group check: Nitro
        -----------------------------
        if is_nitro and c == 2:
            bo[N,O] = bo[O,N] = 1.5
            mmtypes[O] = 'O_R'
            mmtypes[N] = 'N_R'
        if is_nitro and c == 3 :
            bo[N,O] = bo[O,N] = 1.33
            mmtypes[N] = 'N_R'
            mmtypes[O] = 'O_R'
    """
    is_nitro = False

    if atoms[idx].symbol == 'N':
        idx_j = nn[idx].nonzero()[0].tolist()

        symbols_j = numpy.array([a.symbol for a in atoms[idx_j]])
        values, counts = numpy.unique(symbols_j,return_counts=True)
        for s,c in zip(values,counts):
            if s == 'O' and c == 2:
                bo_tmp = 1.5
                mmtypes[idx] = 'N_R'
                is_nitro = True
            if s == 'O' and c == 3:
                bo_tmo = 1.33
                mmtypes[idx] = 'N_R'
                is_nitro = True
        if is_nitro:
            for j in idx_j:
                if atoms[j].symbol == 'O':
                    bo[j,idx] = bo_tmp
                    bo[idx,j] = bo_tmp
                    # Change types to aromatic
                    mmtypes[j] = 'O_R'
    return is_nitro, bo, mmtypes


def get_is_carboxylate(idx,atoms,nn,bo,mmtypes,rules='UFF'):
    """
        Functional group check: Carboxylate
        -----------------------------
        if is_carboxylate and c == 2:
            bo[C,O] = bo[O,C] = 1.5
            mmtypes[C] = 'C_R'
            mmtypes[O] = 'O_R'
        if is_carboxylate and c == 3: 
            bo[C,O] = bo[O,C] = 1.33
            mmtypes[C] = 'C_R'
            mmtypes[O] = 'O_R'
    """
    is_carboxylate = False

    if atoms[idx].symbol == 'C':
        idx_j = nn[idx].nonzero()[0].tolist()

        symbols_j = numpy.array([a.symbol for a in atoms[idx_j]])
        values, counts = numpy.unique(symbols_j,return_counts=True)
        for s,c in zip(values,counts):
            if s == 'O' and c == 2:
                if rules == 'UFF':
                    bo_tmp = 1.5
                    mmtypes[idx] = 'C_R'
                if rules == 'openbabel':
                    bo_tmp = 1.0
                    mmtypes[idx] = 'C_2'
                is_carboxylate = True
            if s == 'O' and c == 3:
                if rules == 'UFF':
                    bo_tmp = 1.33
                    mmtypes[idx] = 'C_R'
                if rules == 'openbabel':
                    bo_tmp = 1
                    mmtypes[idx] = 'C_2'
                is_carboxylate = True
        if is_carboxylate:
            for j in idx_j:
                if atoms[j].symbol == 'O':
                    # Change types to aromatic
                    if rules == 'UFF':
                        mmtypes[j] = 'O_R'
                    if rules == 'openbabel':
                        mmtypes[j] = 'O_2'
                        if j % 2:
                            bo_tmp *=2
                    bo[j,idx] = bo_tmp
                    bo[idx,j] = bo_tmp

    return is_carboxylate, bo, mmtypes

def get_is_enol_ether(idx,atoms,nn,bo,mmtypes):
    """
        Functional group check: Enol Ether 
        -----------------------------
        if is_enol_either: 
            mmtypes[O] = 'O_R'
    """
    is_enol_either = False
    has_O = False
    idx_C = None
    has_C = False
    idx_C = None

    if atoms[idx].symbol == 'C':
        idx_j = nn[idx].nonzero()[0].tolist()
        for j in idx_j:
            sym_j = atoms[j].symbol
            if 'O' == sym_j:
                has_O = True
                idx_O = j
            if 'C' == sym_j:
                has_N = True
                idx_N = j
            if has_O and has_C:
                is_enol_either = True
                # Change types to aromatic 
                mmtypes[idx_O] = 'O_R'
    return is_enol_either, bo,  mmtypes


def get_functional_group_perception(atoms,nn,bo,mmtypes,rules,verbose=3):
    """
        Function group perception 
        -------------------------
    """
    is_amide = numpy.zeros(len(atoms),dtype=bool)
    is_nitro = numpy.zeros(len(atoms),dtype=bool)
    is_carboxylate = numpy.zeros(len(atoms),dtype=bool)
    is_enol_ether = numpy.zeros(len(atoms),dtype=bool)
    # Amide:  O - C - N 
    # (N,C), (C,N) -> BO = 1.41 
    for i in range(len(atoms)):
        if atoms[i].symbol == 'C':
            tmp_is_amide, bo, mmtypes = get_is_amide(i,atoms,nn,bo,mmtypes,rules)
            is_amide[i] = tmp_is_amide
            tmp_is_carboxylate, bo, mmtypes = get_is_carboxylate(i,atoms,nn,bo,mmtypes,rules)
            is_carboxylate[i] = tmp_is_carboxylate
            
            tmp_is_enol_ether, bo, mmtypes = get_is_enol_ether(i,atoms,nn,bo,mmtypes)
            is_enol_ether[i] = tmp_is_enol_ether
            if verbose > 3:
                print(f'is_amide: {tmp_is_amide} {is_amide}')
                print(f'is_carboxylate: {tmp_is_carboxylate} {is_carboxylate}')
                print(f'is_enol_ether: {tmp_is_enol_ether} {is_enol_ether}')
        if atoms[i].symbol == 'N':
            tmp_is_nitro, bo, mmtypes = get_is_nitro(i,atoms,nn,bo,mmtypes)
            is_nitro[i] = tmp_is_nitro
            if verbose > 3:
                print(f'is_nitro: {tmp_is_nitro} {is_nitro}')

    return is_amide, is_nitro, is_carboxylate, is_enol_ether, bo, mmtypes


class FunctionalGroupsPerception:
    """
        FunctionalGroupsPerception class
        --------------------------------
        Adjust molecular mechanics datatypes (mmtypes) 
        and bondo order (bo) 
        for specific chemical groups 
            - amides 
            - nitro 
            - carboylate 
            - enol-ether 
        using specific rules (UFF). 
        If aromatic bonds are in the system the can be described 
        with different bond types (btypes), e.g., LEWIS and LDQ. 
    """
    def __init__(self,atoms,nn,bo,mmtypes,rules,btype,verbose=3):
        """
            __init__ 
            ---------
            Initialize an instance if the class. 
        """
        self.atoms = atoms 
        self.nn = nn 
        self.bo = bo 
        self.mmtypes = mmtypes 
        self.rules = rules 
        self.btype = btype 
        self.verbose = verbose 

    def kernel(self): 
        """
            kernel 
            ------
            Main function for this class. 

            3.a Functional group perception
            3.b Aromatic rings perception

            Input
            -----
            rules: str(), UFF (resonant bonds in 3.a and resonant mmtypes)
                          openbabel (resonant bonds in 3.a no resonant mmtypes)
        """
        # 3.a
        # Functional group perception
        # - check if it is amide
        # - check if it is nitro
        # - check if it is carboxylate
        # - check if it is enol ether
        self.is_amide, self.is_nitro, self.is_carboxylate, self.is_enol_ether, self.bo, self.mmtypes = get_functional_group_perception(self.atoms,self.nn,self.bo,self.mmtypes,rules=self.rules,verbose=self.verbose)
        # 3.b
        # Aromatic rings (5,6 rings)
        self.aromatic, self.mmtypes, self.cycles, self.bo = aromatic_perception(self.atoms,self.nn,self.bo, self.mmtypes,btype=self.btype)
        self.aromatic, self.mmtypes, self.cycles, self.bo = magic_aromatic_perception(atoms=self.atoms,nn=self.nn,bo=self.bo,mmtypes=self.mmtypes,btype=self.btype,verbose=self.verbose)
        ## If we adjust the bo we need to recalculate va.
        #self.va, va_max, tps, ob = check_overbonding(self.atoms,self.bo)
        ## DANGERHANS
        #self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,btype=btype)


