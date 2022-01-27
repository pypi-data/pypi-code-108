import numpy 
from pyflosic2 import Atoms 
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.atoms.bondorder import get_guess_bond_order
from pyflosic2.guess.perception.bonds_perception import clean_overbonding
from pyflosic2.guess.perception.atoms_perception import get_spin 
from pyflosic2.guess.perception.aromatic_perception import aromatic_perception
from pyflosic2.guess.perception.magic_bonds import magic_aromatic_perception
from pyflosic2.guess.perception.core_motifs import CoreMotifs
from pyflosic2.guess.perception.lone_motifs import LoneMotifs
from pyflosic2.guess.perception.bonds_motifs import BondMotifs
from pyflosic2.guess.perception.utils import check_spin 

""" Electron Perception, i.e., determine a FOD guess based on bonding information """

class ElectronPerception:
    """
        ElectronPerception class. 
        -------------------------
        Use given bonding information, i.e., bond order (bo) 
        to generate a electronic configuration where 
        semi-classical positions/ Fermi-orbital descriptors 
        are used to describe the coordinates of electrons. 
    """
    def __init__(self,atoms,nn,bo,va,l,fc,sp,verbose,elec_symbols=['X','He'],btype='LDQ'):
        """
            __init__
            --------
            Initialize an instance of the class. 
        """
        self.atoms = atoms 
        self.nn = nn 
        self.bo = bo 
        self.va = va 
        self.l = l 
        self.fc = fc 
        self.sp = sp 
        self.verbose = verbose 
        self.elec_symbols = elec_symbols 
        self.btype = btype 

    def kernel(self): 
        """

            kernel 
            ------

            Main function for this class. 
            It performs the Electron perception. 
            This conceptional based on the original idea
            of PyLEWIS.

            Workflow
            --------
                - [1] Core electron perception
                - [2] Lone electron perception
                - [3] Bond electron perception
                      - btypes = ['LEWIS','LDQ']
        """
        sym_fod1 = self.elec_symbols[0]
        sym_fod2 = self.elec_symbols[1]
        # fill symbols with nuclei symbols
        symbols = self.atoms.symbols
        # fill positions with nuclei positions
        positions = self.atoms.positions.tolist()
        # For LDQ we are calculating a reference Lewis bo
        # this enables easy assignment of X-He-X vs He-X-He
        if self.btype == 'LDQ' or self.btype == 'LEWIS':
            _, self.bo_ref = get_guess_bond_order(self.atoms)
            _, self.bo_ref = clean_overbonding(self.atoms,self.nn,self.bo_ref,btype='LEWIS')
            self.mmtypes = numpy.zeros(len(self.atoms),dtype=object)
            print(self.atoms,self.nn,self.bo_ref,self.mmtypes,self.btype) 
            _, _, _, bo_ref = aromatic_perception(self.atoms,self.nn,self.bo_ref, self.mmtypes,btype="Lewis",verbose=self.verbose)
            _, _, _, bo_ref = magic_aromatic_perception(atoms=self.atoms,nn=self.nn,bo=self.bo_ref,mmtypes=self.mmtypes,btype="LEWIS")
        #if btype == 'LEWIS':
        #    bo_ref = copy(bo)
        mol_Na = 0
        mol_Nb = 0
        for i in range(len(self.atoms)):
            atom_Na = 0
            atom_Nb = 0
            sym = self.atoms[i].symbol
            pos = self.atoms[i].position
            # N: Total number of electrons
            N = symbol2number[sym]
            # V: Valence number of electrons
            V = self.va[i]
            # R: Radical/lone number of electrons
            R = self.l[i]
            # F: Formal charge
            F = self.fc[i]
            # C: Number of core electrons
            C = N-V-R-F
            if self.verbose > 3:
                print(f'{self.atoms[i].symbol} #core-e- : {C} #valenc-e- {V} #lone-e- {R}')
            # core electron perception
            cm = CoreMotifs(C,self.atoms[i],symbols,positions)
            cm.kernel()
            # update
            symbols = cm.symbols
            positions = cm.positions
            atom_Na += cm._Na
            atom_Nb += cm._Nb
            # lone electron perception
            lm = LoneMotifs(R,i,self.atoms,self.nn,self.sp, symbols, positions)
            lm.kernel()
            # update
            symbols = lm.symbols
            positions = lm.positions
            atom_Na += lm._Na
            atom_Nb += lm._Nb
            # bond electron perception
            idx_j = self.nn[i].nonzero()[0].tolist()
            for j in idx_j:
               if j > i:
                   bm = BondMotifs(self.bo[i,j], self.bo_ref[i,j],self.sp,self.nn, i, j, self.atoms,symbols,positions)
                   #bm._Na = atom_Na
                   #bm._Nb = atom_Nb
                   bm.kernel()
                   # update
                   symbols = bm.symbols
                   positions = bm.positions
                   atom_Na += bm._Na
                   atom_Nb += bm._Nb
            mol_Na += atom_Na
            mol_Nb += atom_Nb
            print(f'Atom: {atom_Na} {atom_Nb}')
        # Check: Na, Nb and M
        Na, Nb, M = check_spin(symbols,elec_symbols=self.elec_symbols)
        M0 = get_spin(self.l)
        if self.verbose > 3:
            print(f'Na : {Na} Nb: {Nb} M : {M} M0 : {M0}')
            print(f'Na : {mol_Na} Nb : {mol_Nb}')
        atoms = Atoms(symbols,positions)
        return atoms

