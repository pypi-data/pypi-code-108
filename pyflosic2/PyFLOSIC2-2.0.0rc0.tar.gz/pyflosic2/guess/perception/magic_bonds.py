import numpy 
from itertools import combinations, permutations
from copy import copy, deepcopy
from pyflosic2.units.constants import covalent_radii
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.guess.perception.DFS import get_DFS_cycles, get_DFS_longest_paths 
from pyflosic2.guess.perception.params import max_coordination, get_max_valence, eval_bond_order 

""" Advanced aka magic rules to optimize bond orders """

def MagicBonds(atoms,verbose=3):
    """
        MagicBonds
        ----------
        Calculate perform a inspired Antechamber
        but modified bond assignment procedure.

        Workflow
        --------
            - [1] determine molecular graph
            - [2] find longest connected paths in molecular graph
            - [3] set trial bond orders until every bond is assigned

        References
        ----------
            - [1]  http://ambermd.org/antechamber/antechamber.pdf

        Input
        -----
        atoms   : Atoms(), Atoms() object/instance
        verbose : int(), verbosity/output level

        Output
        ------
        nn      : numpy.array(), next nearest neighbours numpy array
        bo      : numpy.array(), bond order matrix

    """
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    nn, bonds = get_nn_bonds(atoms,rc=rc)
    if verbose > 3:
        print(f'bonds: {bonds}')
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    bo = numpy.zeros((len(atoms),len(atoms)))
    # molecule as graph
    molgraph = get_molgraph(atoms,nn,verbose=verbose)
    # Determine longest paths in molecular graph
    # using DFS
    longest_paths = get_DFS_longest_paths(G=molgraph)
    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # Loop of longest paths in molgraph
    for path in longest_paths[2]:
        score = get_score(atoms,path)
        if verbose > 3:
            print(f'score: {score}')
        # Loop over connected nodes in path
        for idx in range(len(path)-1):
            # construct connected indicies (i,j)
            # this way we loop over all connected
            # bonds in the path
            i,j = path[idx],path[idx+1]
            b = bonds.get_bond(i,j)
            if b.status == 'unassigned':
                # Loop over trial bond orders
                for bo_trial in [1,2,3]:
                    b_tmp = copy(b)
                    co_tmp = co.copy()
                    va_tmp = va.copy()
                    for idx in [b.i,b.j]:
                        co_tmp[idx] -= 1
                        va_tmp[idx] -= bo_trial
                    if verbose > 3:
                        print(f'iter: co: {co_tmp} va: {va_tmp}')
                    # Check if condition for acceptance is fullfilled
                    # we only update (co,va,bonds)
                    # if conditions are fullfilled
                    if co_tmp[b.i] == 0 and va_tmp[b.i] ==0:
                        # condition fullfilled for b.i
                        b_tmp.status = 'assigned'
                        b_tmp.bo = bo_trial
                        b = copy(b_tmp)
                        co = co_tmp.copy()
                        va = va_tmp.copy()
                        bonds.set_bond(b.i,b.j,b)
                        break
                    if co_tmp[b.j] == 0 and va_tmp[b.j] ==0:
                        # condition fullfilled for b.j
                        b_tmp.status = 'assigned'
                        b_tmp.bo = bo_trial
                        b = copy(b_tmp)
                        co = co_tmp.copy()
                        va = va_tmp.copy()
                        bonds.set_bond(b.i,b.j,b)
                        break

    # Bond order (bo) matrix
    bo = numpy.zeros((len(atoms),len(atoms)))
    for b in bonds:
        if verbose > 3:
            print(b.status,b.bo)
        bo[b.i,b.j] = b.bo
        bo[b.j,b.i] = b.bo
    for i in range(0, len(atoms)):
        # get current coordination per atom
        va[i] = bo[i, :].sum()
    if verbose > 3:
        print(f'bo : \n {bo}')
    return nn, bo, va, bonds


def get_nn_bonds(atoms,rc,eps=0.2,verbose=3):
    """
        Get nn and bonds
        ------------------------------------
        Find nearest neighbours for condition

            r_ij < rc[i] + rc[j] + eps

        and determine bonds.

        Input
        -----
        atoms   : Atoms(), atoms object/instance
        rc      : numpy.array(), covalent radii for symbols in Atoms()
        eps     : float, threshold for condition
        verbose : int(), integer for verbosity/ output level

        Output
        ------
        nn_array : numpy.array(), next nearest neighbours numpy array
        Bonds    : Bonds(), Bonds() object/instance

    """
    bonds = []
    nn_array = numpy.zeros((len(atoms),len(atoms)),dtype=int)
    for i,ni in enumerate(atoms):
        for j,nj in enumerate(atoms):
            if j > i:
                r_ij = numpy.linalg.norm(nj.position-ni.position)
                if r_ij < rc[i] + rc[j] + eps:
                    nn_array[i,j] = j
                    nn_array[j,i] = j
                    bonds.append(Bond(i,j,0))
    if verbose > 3:
        print(nn_array)
    return nn_array, Bonds(bonds)

class Bond:
    """
        Bond class
        ----------
        Class holding bonding information
        for a single bond.

    """
    def __init__(self,i,j,bo):
        self.i = i
        self.j = j
        self.bo = bo
        self.status = 'unassigned'

    def __repr__(self):
        """
            Representation
            --------------
            For usage with, e.g., print(Bond()) .

        """
        return f'Bond:({self.i},{self.j},{self.bo})'


class Bonds:
    """
        Bonds class
        -----------
        Holds all possible bonds for an atoms object.
    """
    def __init__(self,bonds):
        self.bonds = bonds
        self.Nbonds = len(bonds)
        self.unassigned = self.Nbonds
        self.assigned = 0

    def __next__(self):
        next(self.iter)
        return self

    def __iter__(self):
        self.iter = iter(self.bonds)
        return self.iter

    def __repr__(self):
        return f'{[(b.i,b.j,b.bo) for b in self.bonds]}'

    def get_bond(self,i,j):
        """
            Get bond
            --------
            Get bond between atom i and atom j.
        """
        bond = [b for b in self.bonds if (b.i == i and b.j == j) or (b.i == j and b.j == i)] #[0]
        #print(f'bond: {i} {j} {bond} \n {self.bonds}')
        return bond[0]

    def set_bond(self,i,j,bond):
        """
            Set Bond
            --------
            Replace the bond between atom i and atom j
            with a new bond object.
        """
        bonds = numpy.array(self.bonds)
        bonds[bonds == self.get_bond(i,j)] = bond
        self.bonds = bonds.tolist()

def get_molgraph(atoms,nn,verbose=3):
    """
        Get molgraph
        ------------
        Get molecular graph.
    """
    # molecule as graph 
    molgraph = {}
    for i in range(len(atoms)):
        dct_tmp = {i : nn[i].nonzero()[0].tolist()}
        molgraph.update(dct_tmp)
    if verbose > 3:
        print(f'molgraph: {molgraph}')
    return molgraph

def get_score(atoms,path):
    """
        Score
        -----
        Classifier for paths (pi) in a molecular graph.
        If two paths p1 und p2 have the same score
        then they may assumed to be identical.
        Note: This score has nothing to do with tps/aps.
    """
    score = 0
    for i in path:
        ascore = i*0.11 + symbol2number[atoms[i].symbol]*0.08
        score += ascore
    return score

def assign_bond(atoms,nn,bonds,aromatic,bo,i,j,btype='LEWIS'):
    b = bonds.get_bond(i,j)
    #if b.status == 'unassigned' and btype == 'LDQ':
    #    bo_tmp = 1.5 
    #    status_tmp = 'assigned'
    #    bo[i,j] = bo_tmp
    #    bo[j,i] = bo_tmp
    #    b.status = status_tmp
    #    b.bo = bo_tmp
    #    bonds.set_bond(i,j,b)
    #    bonds.set_bond(j,i,b)

    if b.status == 'unassigned':
            set_double = True
            b_nn_j = 0
            b_nn_i = 0
            # check neighbours of node i
            idx_j = nn[i].nonzero()[0].tolist()
            for nnj in idx_j:
                bij= bonds.get_bond(i,nnj)
                if nnj != j:
                    b_nn_j += bij.bo
                # if one neigbour already has bo > 1
                # we may not want to set the current bo > 1
                if bij.bo > 1:
                    set_double = False
            # check neigbours of node j
            idx_i = nn[j].nonzero()[0].tolist()
            for nni in idx_i:
                bji= bonds.get_bond(j,nni)
                if nni != i:
                    b_nn_i += bji.bo
                # if one neigbour already has bo > 1
                # we may not want to set the current bo > 1
                if bji.bo > 1:
                   set_double = False
            print(f'set_double: {set_double} b_nn_j: {b_nn_j} b_nn_i: {b_nn_i}')
            sym_bi = atoms[i].symbol
            max_va = get_max_valence(sym_bi,len(idx_j))
            max_bo_tmp_j = max_va - b_nn_j
            max_bo_tmp_i = max_va - b_nn_i
            if btype == 'LEWIS':
                if max_bo_tmp_j == 2 and set_double == True:
                    bo_tmp = 2
                    status_tmp = 'assigned'
                    aromatic[i] = 1
                    aromatic[j] = 1
                if max_bo_tmp_j == 2 and set_double == False:
                    bo_tmp = 1
                    status_tmp = 'assigned'
                if max_bo_tmp_j ==1:
                    bo_tmp = 1
                    status_tmp = 'assigned'
                    aromatic[i] = 1
                    aromatic[j] = 1
            if btype == 'LDQ':
                print(f'>>>>>>>>>>>>> max_bo_tmp_j : {max_bo_tmp_j}')
                bo_tmp = max_bo_tmp_j # 1.5
                status_tmp = 'assigned'

                if max_bo_tmp_j == 1:
                     bo_tmp = 1
                     status_tmp = 'assigned'
                if max_bo_tmp_j == 1.5:
                     bo_tmp = 1.5
                     status_tmp = 'assigned'
                     aromatic[i] = 1
                     aromatic[j] = 1
                if max_bo_tmp_j == 2:
                     bo_tmp = 2
                     status_tmp = 'assigned'

                #if max_bo_tmp_j == 2 and set_double == True:
                #    bo_tmp = 1.5
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 2.5 and set_double == True:
                #    bo_tmp = 1.5
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 3 and set_double == True:
                #    bo_tmp = 1
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 2 and set_double == False:
                #    bo_tmp = 1
                #    status_tmp = 'assigned'
            print(f'{atoms[bij.i].symbol} {atoms[bij.j].symbol} {bij.status} {bij.bo} max_bo_tmp: {max_bo_tmp_j} bo_tmp: {bo_tmp} max_va: {max_va} ')
            bo[i,j] = bo_tmp
            bo[j,i] = bo_tmp
            b.status = status_tmp
            b.bo = bo_tmp
            bonds.set_bond(i,j,b)
            bonds.set_bond(j,i,b)
    return bonds, aromatic, bo

def magic_aromatic_perception(atoms,nn,bo,mmtypes,btype='LEWIS',verbose=3):
    aromatic = numpy.zeros(len(atoms),dtype=int)
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    nn, bonds = get_nn_bonds(atoms,rc=rc)
    if verbose > 3:
        print(f'bonds: {bonds}')
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    #bo = numpy.zeros((len(atoms),len(atoms)))
    # molecule as graph
    molgraph = get_molgraph(atoms,nn,verbose=verbose)
    # Get unique cycles
    # find 5 rings and 6 rings
    cycles = [path for node in molgraph for path in get_DFS_cycles(molgraph, node, node) if len(path) == 5 or len(path) == 6]
    if not cycles:
        return aromatic, mmtypes, cycles, bo
    cycles = numpy.array(cycles)
    print(f'cycles: {cycles} number cycles : {len(cycles)}')
    sort_cycles = numpy.sort(cycles)
    # find unique cycles/rings
    sorted_unique_cycles, idx = numpy.unique(sort_cycles,axis=0,return_index=True)
    unique_cycles = cycles[idx]
    #print(f'unique_cycles: {unique_cycles} number unique_cycles : {len(unique_cycles)}')
    #u, ind, c = numpy.unique(sort_cycles,return_counts=True,return_index=True)
    #print(u,ind,c)
    #print(atoms[unique_cycles[0].tolist()])
    ##GUI(atoms[u.tolist()])
    #cyclic_atoms = atoms[u.tolist()]
    #cyclic_molgraph = get_molgraph(cyclic_atoms,nn,verbose=verbose)
    #fused_cycles = [path for node in cyclic_molgraph for path in get_DFS_cycles(molgraph, node, node)]
    #fused_cycles = numpy.array(fused_cycles)
    #sort_fused_cycles = numpy.sort(fused_cycles)
    #fused_cycles = [path for node in cyclic_molgraph for path in get_DFS_path(molgraph,node)]
    #print(f'fused cycles: {fused_cycles} len: {fused_cycles} len(cyc_molgraph) : {len(cyclic_molgraph)}')
    #p_max = get_DFS_longest_paths(molgraph,cyclic_molgraph.keys())
    #print(p_max[1])
    # find unique cycles/rings
    #unique,index,counts = numpy.unique(cycles,return_counts=True,return_index=True)
    #sorted_unique_fused_cycles, idx = numpy.unique(sort_fused_cycles,axis=0,return_index=True)
    #unique_fused_cycles = fused_cycles[idx]
    #print(unique_fused_cycles)

    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # Assign for all bonds bo = 1
    # Fill X-H bonds, may correct
    for b in bonds:
        b.bo = 1
        bo[b.i,b.j] = 1
        bo[b.j,b.i] = 1
        if atoms[b.i].symbol == 'H' or atoms[b.j].symbol == 'H':
            b.status = 'assigned'
    # We have now a list of all aromatic cycles.
    # We determine a all permutations of these aromatic cycles.
    # We assign the bond orders starting with different orders of the cycles.
    # We run this as long we find (hopefully) a good tps.
    perm_list = [p for p in permutations(unique_cycles,len(unique_cycles))]
    Nperm = len(perm_list)
    Niter = 0
    tps = 200
    if btype == 'LDQ':
        for unique in unique_cycles:
            print(f'unique_cycle: {unique}')
            # Loop over connected nodes in path
            for idx in range(len(unique)):
                # construct connected indicies (i,j)
                # this way we loop over all connected
                # bonds in the path
                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                b = bonds.get_bond(i,j)
                b.bo = 1.5
                bo[b.i,b.j] = 1.5
                bo[b.j,b.i] = 1.5
                bonds.set_bond(i,j,b)
                bonds.set_bond(j,i,b)
                #aromatic[i] = 1
                #aromatic[j] = 1

    bo_ref = bo.copy()
    bonds_ref = deepcopy(bonds)
    while tps > 0 and Niter < Nperm:
        bo = bo_ref.copy()
        bonds = deepcopy(bonds_ref)
        for unique in perm_list[Niter]:
            print(f'unique_cycle: {unique}')
            # Loop over connected nodes in path
            for idx in range(len(unique)):
                # construct connected indicies (i,j)
                # this way we loop over all connected
                # bonds in the path
                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                bonds, aromatic, bo = assign_bond(atoms,nn,bonds,aromatic,bo,i,j,btype)
                aromatic[i] = 1
                aromatic[j] = 1
        for b in bonds:
            print(f'bond {b.i} {b.j} {atoms[b.i].symbol} {atoms[b.j].symbol} {b.status} {b.bo}')
        tps = eval_bond_order(atoms,nn,bo,verbose=3)
        print(f'>>>>> Niter: {Niter} TPS: {tps}')
        Niter += 1
            #if count > 0:
            #    break

    # After the aromatic perception there can be still
    # unassigned bonds.
    # In principle a more general magicbonds can be applied here.
    # But the iternal logic of magicbonds is different.
    for b in bonds:
        bonds, aromatic, bo = assign_bond(atoms,nn,bonds,aromatic,bo,b.i,b.j)
        print(f'bond {b.i} {b.j} {atoms[b.i].symbol} {atoms[b.j].symbol} {b.status} {b.bo}')
    for i in range(0, len(atoms)):
        # get current coordination per atom
        va[i] = bo[i, :].sum()
    print(f'magic aromatic va: {va}')
    return aromatic, mmtypes, unique_cycles, bo

