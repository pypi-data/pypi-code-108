import numpy 
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.units.constants import covalent_radii

def get_nearest_neighbours(atoms,rc,eps=0.2,verbose=3): #0.2
    """
        Get nearest neighbours (numpy.array)
        ------------------------------------
        Find nearest neighbours for condition 
            
            r_ij < rc[i] + rc[j] + eps 

        
        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        rc      : numpy.array(), covalent radii for symbols in Atoms() 
        eps     : float, threshold for condition 
        verbose : int(), integer for verbosity/ output level

    """
    nn_array = numpy.zeros((len(atoms),len(atoms)),dtype=int)
    for i,ni in enumerate(atoms):
        for j,nj in enumerate(atoms):
            if j > i:
                r_ij = numpy.linalg.norm(nj.position-ni.position)
                if r_ij < rc[i] + rc[j] + eps:
                    nn_array[i,j] = j
                    nn_array[j,i] = j
    if verbose > 3:
        print(nn_array)
    return nn_array

def get_guess_bond_order(atoms):
    """
        Get guess bond order 
        --------------------
        Using nearst neighbours (numpy.arrays) 
        with different cutoffs (rc1, rc2, rc3) 
        for (single, double, triple) bonds 
        we guess the bond order matrix (bo).

        Rules 
        -----
            - Hydrogen bond order is set to 1 

        Input
        -----
        atoms   : Atoms(), atoms object/instance

        Notes
        -----
            - origionally placed at perception.py 
    """
    symbols = numpy.array(atoms.symbols)
    rc1 = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    rc2 = rc1 - 0.15 # 0.15
    rc3 = rc2 - 0.10 # 0.1 0.15
    # single bonds 
    nn1 = get_nearest_neighbours(atoms=atoms,rc=rc1)
    # double bonds 
    nn2 = get_nearest_neighbours(atoms=atoms,rc=rc2)
    # triple bonds 
    nn3 = get_nearest_neighbours(atoms=atoms,rc=rc3)
    NN = [nn1,nn2,nn3]

    # bond order (bo) matrix
    bo = numpy.zeros((len(atoms), len(atoms)))
    hydrogens = symbols == "H"
    for i,ni in enumerate(atoms.positions):
        idx1 = nn1[i].nonzero()[0].tolist()
        idx2 = nn2[i].nonzero()[0].tolist()
        idx3 = nn3[i].nonzero()[0].tolist()
        if idx1:
            bo[i,idx1] = 1.0
        if idx2:
            bo[i,idx2] = 2.0
        if idx3:
            bo[i,idx3] = 3.0
    # Hydrogen bond order 
    bo_h = bo[hydrogens]
    bo_h[bo_h > 1.0] = 1.0
    bo[hydrogens, :] = bo_h
    bo[:, hydrogens] = bo_h.T
    return nn1, bo
