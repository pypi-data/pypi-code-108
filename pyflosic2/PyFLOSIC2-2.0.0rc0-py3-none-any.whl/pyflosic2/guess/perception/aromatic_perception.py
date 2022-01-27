import numpy 
from itertools import combinations, permutations
from pyflosic2.guess.perception.DFS import get_DFS_cycles

def aromatic_perception(atoms,nn,bo,mmtypes,btype='LEWIS',verbose=3):
    """
        Get aromatic perception 
        -----------------------
        Determine aromatic rings in atoms. 

        Workflow 
            - [1] find cycles (5,6 ring) in molecular graph 
            - [2] check coplanarity 
            - [3] use LDQ bo to check bo_ij == 1.5 
    """
    aromatic = numpy.zeros(len(atoms),dtype=int)
    visited = numpy.zeros(len(atoms),dtype=int)
    # molecule as graph 
    molgraph = {}
    for i in range(len(atoms)):
        dct_tmp = {i : nn[i].nonzero()[0].tolist()}
        molgraph.update(dct_tmp)
    # find 5 rings and 6 rings 
    cycles = [path for node in molgraph for path in get_DFS_cycles(molgraph, node, node) if len(path) == 5 or len(path) == 6]
    print(f'cycles: {cycles}')
    if not cycles:
        print("No aromatic cycles determined.")
        return aromatic, mmtypes, cycles, bo
    cycles = numpy.array(cycles)
    sort_cycles = numpy.sort(cycles)
    # find unique cycles/rings 
    #unique,index,counts = numpy.unique(cycles,return_counts=True,return_index=True) 
    sorted_unique_cycles, idx  =numpy.unique(sort_cycles,axis=0,return_index=True)
    unique_cycles = cycles[idx]

    for unique in unique_cycles:
        print(f'cycle: {unique}')
        # check coplanarity 
        # are combinations of 4 points from ring/cycle 
        # in one plane? 
        pos = atoms[unique.tolist()].positions
        dets = numpy.array([numpy.linalg.det(numpy.array(x[:3]) - x[3]) for x in combinations(pos, 4)])
        eps = 0.1
        coplanar = (dets < eps).all()
        print(f'coplanar: {coplanar}')
        if coplanar:
            for idx in range(len(unique)):
            # construct connected indicies (i,j)
            # this way we loop over all connected
            # bonds in the path
                #if visited[i] == 1:
                #   check_idx_j = nn[i].nonzero()[0] 
                #   co = len(check_idx_j) 
                #   check_idx_j = (check_idx_j[check_idx_j!= j]).tolist()
                #   ve = get_max_valence(atoms[i].symbol,co)
                #   bo_j = bo[i,check_idx_j].sum()
                #   print(f'visited[i]: {i} {j} {check_idx_j} {bo[i,check_idx_j].sum()} {ve}')
                #if visited[i] == 0: 
                #   bo_j = 0
                #   check_idx_j = nn[i].nonzero()[0]
                #   co = len(check_idx_j)
                #   ve = get_max_valence(atoms[i].symbol,co)

                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                if btype == 'LDQ':
                    bo[i,j] = 1.5
                    bo[j,i] = 1.5
                if btype == 'LEWIS':
                    if idx % 2:
                        bo_tmp = 1
                    if not idx % 2:
                        bo_tmp = 2
                    #if bo_j + bo_tmp > ve or bo_j + bo_tmp < ve: 
                    #    print('adjusted by condition')
                    #    bo_tmp = ve - bo_j
                    #    print(f'adjusted by condition: bo_tmp {bo_tmp} ve {bo_j+bo_tmp} vmax {ve}')
                    #print(f'captain lewis : {i} {j} {bo_tmp}')
                    bo[i,j] = bo_tmp
                    bo[j,i] = bo_tmp
                mmtypes[i] = atoms[i].symbol +'_R'
                mmtypes[j] = atoms[j].symbol +'_R'
                aromatic[i] = 1
                aromatic[j] = 1
                # 
                visited[i] = 1
    if verbose > 3:
        print(aromatic,mmtypes)
    return aromatic, mmtypes, unique_cycles, bo

