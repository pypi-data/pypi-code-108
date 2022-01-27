from pyflosic2 import GUI
from pyflosic2.systems.uflosic_systems import C6H6,H2O,CH4, COH2
from pyflosic2.ff.uff_systems import *
from pyflosic2.guess.pyperception import Perception 
from pyflosic2.ff.uff import uff_energy,check,UFF

# Benchmark sets 
# UFF benchmark
# - A benchmark set used in the UFF article 
uff_systems = ['Conformer3D_CID_6334',  # C, H
               'Conformer3D_CID_8252',  # C, H
               'Conformer3D_CID_7845',  # C, H 
               'Conformer3D_CID_6335',  # C, H 
               'Conformer3D_CID_674',   # N 
               'Conformer3D_CID_1146',  # N 
               'Conformer3D_CID_142199',# N 
               'Conformer3D_CID_6342',  # N 
               'Conformer3D_CID_14055', # N 
               'Conformer3D_CID_7855',  # N 
               'Conformer3D_CID_8254',  # O 
               'Conformer3D_CID_10903', # O 
               'Conformer3D_CID_7861',  # O 
               'Conformer3D_CID_177',   # O 
               'Conformer3D_CID_180',   # O 
               'Conformer3D_CID_12222', # O 
               'Conformer3D_CID_7847',  # O 
               'Conformer3D_CID_7865',
               'Conformer3D_CID_178',   # N 
               'Conformer3D_CID_31254'] # N 

# PyFLOSIC KnightValley benchmark
# - A benchmark set used in PyFLOSIC2 
knight_valley = ['H2O','CH4','COH2']


def bench_C6H6():
    """
        bench_C6H6
        ----------
        Benchmark/test various configurations for C6H6 (benzene). 
    """
    rv1 = run('C6H6',btype='LDQ',rules='openbabel',verbose=3)                        
    rv2 = run('Conformer3D_CID_10903',btype='LDQ',rules='openbabel',verbose=3)       
    rv3 = run('H2O_KT',btype='LDQ',rules='openbabel',verbose=4)                      
    rv4 = run('Conformer3D_CID_7855_KT',btype='LEWIS',rules='openbabel',verbose=4)   
    rv5 = run('Conformer3D_CID_7865',btype='LEWIS',rules='openbabel',verbose=4)      
    RV = [rv1,rv2,rv3,rv4,rv5] 
    for rv in RV:
        my_pprint(rv)

def bench_CH():
    """
        bench_CH
        --------
        Benchmark/test various systems containing C-H. 
    """
    rv1 = run('Conformer3D_CID_6334',btype='LEWIS',rules='openbabel',verbose=4)      
    rv2 = run('Conformer3D_CID_8252',btype='LEWIS',rules='openbabel',verbose=4)      
    rv3 = run('Conformer3D_CID_7845',btype='LEWIS',rules='openbabel',verbose=4)      
    rv4 = run('Conformer3D_CID_6335',btype='LEWIS',rules='openbabel',verbose=4)      
    RV = [rv1,rv2,rv3,rv4]
    for rv in RV:
        my_pprint(rv)

def bench_O():
    """
        bench_O
        -------
        Benchmark/test various systems containing O.
    """
    rv1 = run('Conformer3D_CID_8254',btype='LEWIS',rules='openbabel',verbose=4)      
    rv2 = run('Conformer3D_CID_10903',btype='LEWIS',rules='openbabel',verbose=4)     
    rv3 = run('Conformer3D_CID_7861',btype='LEWIS',rules='openbabel',verbose=4)      
    rv4 = run('Conformer3D_CID_177',btype='LEWIS',rules='openbabel',verbose=4)       
    rv5 = run('Conformer3D_CID_180',btype='LEWIS',rules='openbabel',verbose=4)       
    rv6 = run('Conformer3D_CID_12222',btype='LEWIS',rules='openbabel',verbose=4)     
    rv7 = run('Conformer3D_CID_7847',btype='LEWIS',rules='openbabel',verbose=4)      
    rv8 = run('Conformer3D_CID_7865',btype='LEWIS',rules='openbabel',verbose=4)      
    RV = [rv1,rv2,rv3,rv4,rv5,rv6,rv7,rv8]
    for rv in RV:
        my_pprint(rv)

def bench_N():
    """
        bench_N
        -------
        Benchmark/test various systems containing N.
    """
    rv1 = run('Conformer3D_CID_674',btype='LEWIS',rules='openbabel',verbose=4)       
    rv2 = run('Conformer3D_CID_1146',btype='LEWIS',rules='openbabel',verbose=4)      
    rv3 = run('Conformer3D_CID_142199',btype='LEWIS',rules='openbabel',verbose=4)    
    rv4 = run('Conformer3D_CID_6342',btype='LEWIS',rules='openbabel',verbose=4)      
    rv5 = run('Conformer3D_CID_14055',btype='LEWIS',rules='openbabel',verbose=4)     
    rv6 = run('Conformer3D_CID_7855',btype='LEWIS',rules='openbabel',verbose=4)      
    rv7 = run('Conformer3D_CID_178',btype='LEWIS',rules='openbabel',verbose=4)       
    rv8 = run('Conformer3D_CID_31254',btype='LEWIS',rules='openbabel',verbose=4)     
    RV = [rv1,rv2,rv3,rv4,rv5,rv6,rv7,rv8]
    for rv in RV:
        my_pprint(rv)

def bench_aromatics():
    """
        NOTABENE: NOT WORKING!
        bench_aromatics
        ---------------
        Benchmark/test various aromatic systems.
    """
    # Aromatics
    Lewis = run('C6H6',btype='LEWIS',rules='openbabel',verbose=4)              # KT: E_bond off
    LDQ = run('C6H6',btype='LDQ',rules='openbabel',verbose=4)                  # KT: Fine
    print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_931',btype='LEWIS',rules='openbabel',verbose=4)   # KT: no good
    #LDQ = run('Conformer3D_CID_931',btype='LDQ',rules='openbabel',verbose=4)       # KT: not quite right, but close
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    ## Trans-sibelene
    #Lewis = run('Conformer3D_CID_638088',btype='LEWIS',rules='openbabel',verbose=4)    # KT: no good
    #LDQ = run('Conformer3D_CID_638088',btype='LDQ',rules='openbabel',verbose=4)        # KT: Fine
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_9115',btype='LEWIS',rules='openbabel',verbose=4)      # KT: no good
    #LDQ = run('Conformer3D_CID_9115',btype='LDQ',rules='openbabel',verbose=4)          # KT: also off
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_8418',btype='LEWIS',rules='openbabel',verbose=4)      # KT: no good
    #LDQ = run('Conformer3D_CID_8418',btype='LDQ',rules='openbabel',verbose=4)          # KT: Slightly off
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_31423',btype='LEWIS',rules='openbabel',verbose=4)     # KT: no good
    #LDQ = run('Conformer3D_CID_31423',btype='LDQ',rules='openbabel',verbose=4)         # KT: no good
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')


def my_pprint(rv):
    """
        my_pprint
        A shorthand for a specific printing function
    """
    print('{}: Etot - Etot,ref: {}, mmtypes - mmtypes,ref: {}'.format(rv[0],rv[1],rv[2]))

def run(key,btype='LEWIS',rules='openbabel',verbose=3):
    """
        run
        ---
        Run a molecular perception for a Atoms object 
        initialized by the system key.  

    """
    # Atoms
    atoms = eval(key)()
    
    # Molecular perception
    mp = Perception(atoms,btype=btype,rules=rules,verbose=verbose)
    bo, mmtypes = mp.kernel()
    print(mp.ap.bo,mp.fp.bo)

    #GUI(mp.atoms)

    # UFF energy
    # mmtypes = ref_openbabel[f_name]['mmtypes']
    ff = UFF(atoms,bo,mmtypes)
    ff.kernel()
    e_check, mm_check = check(key,ff,ref_openbabel)
    return key, e_check, mm_check, ff

def run_all(systems,btype='LEWIS',rules='openbabel',verbose=3):
    """
        run_all: systems
        ----------------
    """
    RV = []
    for key in systems:
        print(f"key: {key}")
        rv = run(key,btype=btype,rules=rules,verbose=verbose)
        RV.append(rv)
    for rv in RV:
        my_pprint(rv)


def main():
    """
        main
        ----
        Main function to test this routine. 
    """
    systems = [knight_valley, uff_systems][-1]
    run_all(systems=systems,btype='LEWIS',rules='openbabel',verbose=4)

def debug():
    """
        debug 
        -----
        Debug function to further develop this routine. 
    """
    #run(f_name="Conformer3D_CID_142199",btype='LEWIS',rules='openbabel')
    bench_C6H6()
    bench_CH()
    bench_O() 
    bench_N()
    bench_aromatics()

if __name__ == "__main__": 
    main() 
    #debug()

