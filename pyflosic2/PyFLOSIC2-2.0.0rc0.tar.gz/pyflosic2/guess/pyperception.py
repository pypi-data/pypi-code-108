import numpy 
from pyflosic2.io.flosic_io import atoms2flosic
from pyflosic2.guess.perception.bonds_perception import BondsPerception 
from pyflosic2.guess.perception.atoms_perception import AtomsPerception 
from pyflosic2.guess.perception.functional_groups_perception import FunctionalGroupsPerception
from pyflosic2.guess.perception.electron_perception import ElectronPerception 
from pyflosic2.io.flosic_io import write_xyz

class Perception():
    """
        Perception class
        ----------------
        Completly automatic molecular perception
        to generate 
            - molecular mechanics datatypes (UFF) 
            - semi-classical electron positions 


        References
        ----------
            - [1] For general workflow: Automatic molecular perception using UFF
                  https://onlinelibrary.wiley.com/doi/epdf/10.1002/jcc.24309?saml_referrer
                  https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fjcc.24309&file=jcc24309-sup-0001-suppinfo.pdf
                  Journal of Computational Chemistry 2016, 37, 1191–1205 1197
            - [2] For: get_guess_bonding_matrix()
                  https://github.com/DCoupry/autografs
                  autografs/utils/mmanalysis.py

        Workflow
        --------
            - [1] Bonds perception
            - [2] Atoms perception
            - [3] Functional groups perception
            - [4] Electron perception 

        Output
        ------
        nn: numpy.array, next nearest neighbours
            len(atoms)
        co: numpy.array, atomic coordination number
            len(atoms)
        va: numpy.array, atomic valence
            len(atoms)
        bo: numpy.array, bond order matrix
            len(atoms)xlen(atoms)
        tps: int() or nodef, total penality score for bo
             goal is tps == 0
        l : numpy.array, lone electrons
            len(atoms)
        sp: numpy.array, sp hybridization

        TODO
        ----
            - Special case: N in planar geometry
            - Special case: bond order bo = 1.41

    """
    def __init__(self,atoms,**kwargs):
        """
            __init__ 
            Initialize an instance of the class. 
        """
        # We only need nuclei information
        [nuclei,fod1,fod2] = atoms2flosic(atoms)
        self.atoms = nuclei
        self._set_kwargs(kwargs)
    
    def _set_kwargs(self,kwargs): 
        """
            set_kwargs
            ----------
            Set secondary input arguments. 
        """
        self.verbose = kwargs.get("verbose",3) 
        self.bo_status = kwargs.get("bo_status","incorrect") 
        self.btype = kwargs.get("btype","LEWIS") 
        self.rules = kwargs.get("rules","UFF") 
        self.elec_symbols= kwargs.get("elec_symbols",["X","He"])

    def _bonds_perception(self):
        """
            _bonds_perception
            -----------------
            1.a Bond detection
            1.b Bond assignment 
                - 1st simple: get_guess_bond_order 
                - 2nd advanced: magicbonds 
            1.c Bond order anlysis
            if tps != 0: 
                1.b (advanced) and 1.c 

        """
        bp = BondsPerception(atoms=self.atoms,
                             bo_status=self.bo_status,
                             btype=self.btype,
                             verbose=self.verbose)
        bp.kernel() 
        self.bp = bp 

    def _atoms_perception(self):
        """
            _atoms_perception
            -----------------
            2.a Hybridization and metal center geometries
            2.b Oxidation numbers computation
            2.c Atom types assignment
            2.d Charge and spin computation 
        """
        ap = AtomsPerception(atoms=self.atoms,
                             nn=self.bp.nn,
                             co=self.bp.co,
                             va=self.bp.va,
                             bo=self.bp.bo,
                             verbose=self.verbose) 
        ap.kernel()
        self.ap = ap 

    def _functional_groups_perception(self): 
        """
            _functional_groups_perception
            -----------------------------
            3.a Functional group perception
            3.b Aromatic rings perception

            Input
            -----
            rules: str(), UFF (resonant bonds in 3.a and resonant mmtypes)
                          openbabel (resonant bonds in 3.a no resonant mmtypes)
        """
        fp = FunctionalGroupsPerception(atoms=self.atoms, 
                                        nn = self.bp.nn, 
                                        bo = self.ap.bo,
                                        mmtypes = self.ap.mmtypes,
                                        rules = self.rules,
                                        btype = self.btype,
                                        verbose = self.verbose) 
        fp.kernel() 
        self.fp = fp 

    def _electron_perception(self):
        """
            _electron_perception
            --------------------
            4.a Electron perception
            This step produce a electronic geometry, 
            which can be used within FLO-SIC. 
        """
        ep = ElectronPerception(atoms=self.atoms,
                                nn=self.bp.nn,
                                bo=self.fp.bo,
                                va=self.ap.va,
                                l=self.ap.l,
                                fc=self.ap.fc,
                                sp=self.ap.sp,
                                verbose=self.verbose,
                                elec_symbols=self.elec_symbols,
                                btype=self.btype)
        self.atoms = ep.kernel()
        self.ep = ep 


    def _write_xyz(self,f_name='perception'):
        """
            _write_xyz
            Write the iternal atoms instance to 
            a xyz file. 
        """
        write_xyz(self.atoms,f'{f_name}.xyz')


    def kernel(self):
        """
            Kernel function
            ---------------
        """
        self._bonds_perception()
        print(f"bo: {self.bp.bo}")
        self._atoms_perception()
        self._functional_groups_perception()
        self._electron_perception()
        return self.fp.bo, self.fp.mmtypes


def main():
    """
        main 
        Main function to test this routine. 
    """
    from pyflosic2.systems.uflosic_systems import C6H6,H2O,CH4, COH2
    from pyflosic2 import GUI
    atoms = C6H6() #CH4() #COH2() #H2O() 
    verbose = 3 
    mp = Perception(atoms)
    bo, mmtypes = mp.kernel()
    print(bo,mmtypes) 
    GUI(mp.atoms) 

if __name__ == "__main__": 
    main() 

