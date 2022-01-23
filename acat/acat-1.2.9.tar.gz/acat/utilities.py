from ase.data import covalent_radii, atomic_numbers, atomic_masses
from ase.geometry.geometry import _row_col_from_pdist
from ase.geometry import find_mic
from ase.formula import Formula
from itertools import product, permutations, combinations
from scipy.spatial.distance import cdist, euclidean
from collections import abc, Counter
import networkx as nx
import numpy as np
import scipy
import math


def neighbor_shell_list(atoms, dx=0.3, neighbor_number=1, 
                        different_species=False, mic=False,
                        radius=None, span=False):
    """Make dict of neighboring shell atoms for both periodic and 
    non-periodic systems. Possible to return neighbors from defined 
    neighbor shell e.g. 1st, 2nd, 3rd by changing the neighbor number.
    Essentially returns a unit disk (or ring) graph.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    dx : float, default 0.3
        Buffer to calculate nearest neighbor pairs.

    neighbor_number : int, default 1
        Neighbor shell number.

    different_species : bool, default False
        Whether each neighbor pair are different species.

    mic : bool, default False
        Whether to apply minimum image convention. Remember to set 
        mic=True for periodic systems.

    radius : float, default None 
        The radius of each shell. Works exactly as a conventional 
        neighbor list when specified. If not specified, use covalent 
        radii instead.

    span : bool, default False
        Whether to include all neighbors spanned within the shell.
        Returns a unit disk graph if True, otherwise returns a unit
        ring graph.

    """

    natoms = len(atoms)
    if natoms == 1:
        return {0: []}
    cell = atoms.cell
    positions = atoms.positions
    nums = set(atoms.numbers)
    pairs = product(nums, nums)
    if not radius:
        cr_dict = {(i, j): (covalent_radii[i] + covalent_radii[j]) for i, j in pairs}
    
    ds = atoms.get_all_distances(mic=mic)
    conn = {k: [] for k in range(natoms)}
    for atomi in atoms:
        for atomj in atoms:
            i, j = atomi.index, atomj.index
            if i != j:
                if not (different_species & (atomi.symbol == atomj.symbol)):
                    d = ds[i,j]
                    crij = 2 * radius if radius else cr_dict[(atomi.number, atomj.number)] 

                    if neighbor_number == 1 or span:
                        d_max1 = 0.
                    else:
                        d_max1 = (neighbor_number - 1) * crij + dx

                    d_max2 = neighbor_number * crij + dx

                    if d > d_max1 and d < d_max2:
                        conn[atomi.index].append(atomj.index)

    return conn


def get_adj_matrix(neighborlist):
    """Returns an adjacency matrix from a neighborlist object.

    Parameters
    ----------
    neighborlist : dict
        A neighborlist (dictionary) that contains keys of each 
        atom index and values of their neighbor atom indices.

    """ 

    conn_mat = []
    index = range(len(neighborlist.keys()))
    # Create binary matrix denoting connections.
    for index1 in index:
        conn_x = []
        for index2 in index:
            if index2 in neighborlist[index1]:
                conn_x.append(1)
            else:
                conn_x.append(0)
        conn_mat.append(conn_x)

    return np.asarray(conn_mat)


def get_mic(p1, p2, cell, pbc=[1,1,0], 
            max_cell_multiple=1e5, 
            return_squared_distance=False): 
    """A highly efficient function for getting all vectors from p1
    to p2. Also able to calculate the squared distance using the 
    minimum image convention (mic). This function is useful when you 
    want to constantly calculate mic between two given positions. 
    Please use ase.geometry.find_mic if you want to calculate an 
    array of vectors all at a time (useful for e.g. neighborlist).  

    Parameters
    ----------
    p1 : numpy.array
        The 3D Cartesian coordinate of the position 1.

    p2 : numpy.array
        The 3D Cartesian coordinate of the position 2.

    cell : numpy.array
        The 3D parallel epipedal unit cell.

    pbc : numpy.array or list, default [1, 1, 0]
        Whether cell is periodic in each direction.

    max_cell_multiple : int, default 1e5
        A large number to account for the maximum repetitions of each 
        of the lattice vectors. The minimum number of repetitions is
        hence calculated by the algorithm using the intersection of a 
        sphere and the unit cell.

    return_squared_distance : bool, default False
        Whether to return the squared mic distance instead of the
        mic vector.
    
    """

    # Precompute some useful values
    a, b, c = cell[0], cell[1], cell[2]
    vol = np.abs(a @ np.cross(b, c))
    a_cross_b = np.cross(a, b)
    a_cross_b_len = np.linalg.norm(a_cross_b)
    a_cross_b_hat = a_cross_b / a_cross_b_len
    b_cross_c = np.cross(b, c)
    b_cross_c_len = np.linalg.norm(b_cross_c)
    b_cross_c_hat = b_cross_c / b_cross_c_len
    a_cross_c = np.cross(a, c)
    a_cross_c_len = np.linalg.norm(a_cross_c)
    a_cross_c_hat = a_cross_c / a_cross_c_len

    # TODO: Wrap p1, and p2 into the current unit cell
    dr = p2 - p1
    min_dr_sq = dr @ dr
    min_length = math.sqrt(min_dr_sq)
    a_max = math.ceil(min_length / vol * b_cross_c_len)
    a_max = min(a_max, max_cell_multiple)
    b_max = math.ceil(min_length / vol * a_cross_c_len)
    b_max = min(b_max, max_cell_multiple)
    if not pbc[2]:
        c_max = 0
    else:
        c_max = math.ceil(min_length / vol * a_cross_b_len)
        c_max = min(c_max, max_cell_multiple)

    min_dr = dr
    for i in range(-a_max, a_max + 1):
        ra = i * a
        for j in range(-b_max, b_max + 1):
            rab = ra + j * b
            for k in range(-c_max, c_max + 1):
                if i == 0 and j == 0 and k == 0:
                    continue
                out_vec = rab + k * c + dr
                len_sq = out_vec @ out_vec 
                if len_sq < min_dr_sq:
                    min_dr = out_vec
                    min_dr_sq = len_sq
    if not return_squared_distance:
        return min_dr

    else:
        return np.sum(min_dr**2)


def expand_cell(atoms, cutoff=None, padding=None):

    #Return Cartesian coordinates atoms within a supercell
    #which contains repetitions of the unit cell which contains
    #at least one neighboring atom. Borrowed from Catkit.
    cell = atoms.cell
    pbc = [1, 1, 0]
    pos = atoms.positions

    if padding is None and cutoff is None:
        diags = np.sqrt((([[1, 1, 1],
                           [-1, 1, 1],
                           [1, -1, 1],
                           [-1, -1, 1]]
                           @ cell)**2).sum(1))

        if pos.shape[0] == 1:
            cutoff = max(diags) / 2.
        else:
            dpos = (pos - pos[:, None]).reshape(-1, 3)
            Dr = dpos @ np.linalg.inv(cell)
            D = (Dr - np.round(Dr) * pbc) @ cell
            D_len = np.sqrt((D**2).sum(1))

            cutoff = min(max(D_len), max(diags) / 2.)

    latt_len = np.sqrt((cell**2).sum(1))
    V = abs(np.linalg.det(cell))
    padding = pbc * np.array(np.ceil(cutoff * np.prod(latt_len) /
                                     (V * latt_len)), dtype=int)

    offsets = np.mgrid[-padding[0]:padding[0] + 1,
                       -padding[1]:padding[1] + 1,
                       -padding[2]:padding[2] + 1].T
    tvecs = offsets @ cell
    coords = pos[None, None, None, :, :] + tvecs[:, :, :, None, :]

    ncell = np.prod(offsets.shape[:-1])
    index = np.arange(len(atoms))[None, :].repeat(ncell, axis=0).flatten()
    coords = coords.reshape(np.prod(coords.shape[:-1]), 3)
    offsets = offsets.reshape(ncell, 3)

    return index, coords, offsets


def hash_composition(nodes):
    """A hashing function to generate an unique identifier of the 
    composition considering self-symmetry. Note that this function 
    only accepts a sequence of connected nodes.
    """
    start = min(nodes)
    starts = [i for i,v in enumerate(nodes) if v == start]
    return min([*nodes[i::d],*nodes[:i:d]] for d in (1,-1) for i in starts)


def bipartitions(shells, total):

    n = len(shells)
    for k in range(n + 1):
        for combo in combinations(range(n), k):
            if sum(len(shells[i]) for i in combo) == total:
                set_combo = set(combo)
                yield sorted(shells[i] for i in combo), sorted(
                shells[i] for i in range(n) if i not in set_combo)
       
                                                                       
def partitions_into_totals(shells, totals):

    assert totals
    if len(totals) == 1:
        yield [shells]
    else:
        for first, remaining_shells in bipartitions(shells, totals[0]):
            for rest in partitions_into_totals(remaining_shells, totals[1:]):
                yield [first] + rest


def get_close_atoms(atoms, cutoff=0.5, mic=False, delete=False):
    """Get a list of close atoms and delete one set of them if requested.
    Identify all atoms that lie within the cutoff radius of each other.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    cutoff : float, default 0.5
        The cutoff radius. Two atoms are too close if the distance between
        them is less than this cutoff

    mic : bool, default False
        Whether to apply minimum image convention. Remember to set 
        mic=True for periodic systems.

    delete : bool, default False
        Whether to delete one set of the close atoms.

    """

    res = np.asarray(list(combinations(np.asarray(range(len(atoms))),2)))
    indices1, indices2 = res[:, 0], res[:, 1]
    p1, p2 = atoms.positions[indices1], atoms.positions[indices2]                      
    if mic:
        _, dists = find_mic(p2 - p1, atoms.cell, pbc=True)
    else:
        dists = np.linalg.norm(p2 - p1, axis=1) 

    dup = np.nonzero(dists < cutoff)
    rem = np.array(_row_col_from_pdist(len(atoms), dup[0]))
    if delete:
        if rem.size != 0:
            del atoms[rem[:, 0]]
    else:
        return rem


def atoms_too_close(atoms, cutoff=0.5, mic=False):
    """Check if there are atoms that are too close to each other.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    cutoff : float, default 0.5
        The cutoff radius. Two atoms are too close if the distance between
        them is less than this cutoff

    mic : bool, default False
        Whether to apply minimum image convention. Remember to set 
        mic=True for periodic systems.

    """

    res = np.asarray(list(combinations(np.asarray(range(len(atoms))), 2)))
    indices1, indices2 = res[:, 0], res[:, 1]
    p1, p2 = atoms.positions[indices1], atoms.positions[indices2]
    if mic:
        _, dists = find_mic(p2 - p1, atoms.cell, pbc=True)
    else:
        dists = np.linalg.norm(p2 - p1, axis=1)

    return any(dists < cutoff)


def atoms_too_close_after_addition(atoms, n_added, cutoff=1.5, mic=False): 
    """Check if there are atoms that are too close to each other after 
    adding some new atoms.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    n_added : int
        Number of newly added atoms.

    cutoff : float, default 1.5
        The cutoff radius. Two atoms are too close if the distance between
        them is less than this cutoff

    mic : bool, default False
        Whether to apply minimum image convention. Remember to set 
        mic=True for periodic systems.

    """

    newp, oldp = atoms.positions[-n_added:], atoms.positions[:-n_added]
    newps = np.repeat(newp, len(oldp), axis=0)
    oldps = np.tile(oldp, (n_added, 1))
    if mic:
        _, dists = find_mic(newps - oldps, atoms.cell, pbc=True)
    else:
        dists = np.linalg.norm(newps - oldps, axis=1)

    return any(dists < cutoff)


def get_angle_between(v1, v2):
    """Returns the angle in radians between vectors 'v1' and 'v2'.

    Parameters
    ----------
    v1 : numpy.array
        Vector 1.
    v2 : numpy.array
        Vector 2.

    """

    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)

    return np.arccos(np.clip(v1_u @ v2_u, -1., 1.))


def get_rejection_between(v1, v2):
    """Calculate the vector rejection of vector 'v1' perpendicular 
    to vector 'v2'.

    Parameters
    ----------
    v1 : numpy.array
        Vector 1.
    v2 : numpy.array
        Vector 2.

    """

    return v1 - v2 * (v1 @ v2) / (v2 @ v2)


def get_rotation_matrix(v1, v2):
    """Return the rotation matrix R that rotates unit vector v1 onto 
    unit vector v2.
 
    Parameters
    ----------
    v1 : numpy.array
        Vector 1.
    v2 : numpy.array
        Vector 2.
 
    """
 
    ax, ay, az = v1[0], v1[1], v1[2]
    bx, by, bz = v2[0], v2[1], v2[2]
    au = v1 / (np.sqrt(ax * ax + ay * ay + az * az))
    bu = v2 / (np.sqrt(bx * bx + by * by + bz * bz))
 
    R = np.asarray([[bu[0] * au[0], bu[0] * au[1], bu[0] * au[2]], 
                    [bu[1] * au[0], bu[1] * au[1], bu[1] * au[2]], 
                    [bu[2] * au[0], bu[2] * au[1], bu[2] * au[2]]])
    return R


def get_rodrigues_rotation_matrix(axis, angle):
    """Return the Rodrigues rotation matrix associated with 
    counter-clockwise rotation about the given axis by an angle.
 
    Parameters
    ----------
    axis : numpy.array
        The axis (vector) to rotate around with.
    angle : numpy.array
        The angle (in radians) to rotate around.
 
    """

    return scipy.linalg.expm(np.cross(np.eye(3),
           axis / np.linalg.norm(axis) * angle))


def get_total_masses(symbol):
    """Get the total molar mass given the chemical symbol of a 
    molecule.

    Parameters
    ----------
    symbol : str
        Chemical symbol of the molecule.

    """

    return np.sum([atomic_masses[atomic_numbers[s]] 
                   for s in list(Formula(symbol))])


def is_list_or_tuple(obj):
    return (isinstance(obj, abc.Sequence)
            and not isinstance(obj, str))


def get_depth(l):
    if isinstance(l, list):
        return 1 + max(get_depth(i) for i in l)
    else:
        return 0

def string_fragmentation(adsorbate):
    """A function for generating a fragment list (list of strings) 
    from a given adsorbate (string).

    Parameters
    ----------
    adsorbate : str
        The string of the adsorbate molecule.

    """
    if adsorbate == 'H2':
        return ['H', 'H']
    sym_list = list(Formula(adsorbate))
    nsyms = len(sym_list)
    frag_list = []
    for i, sym in enumerate(sym_list):
        if sym != 'H':
            j = i + 1
            if j < nsyms:
                hlen = 0
                while sym_list[j]  == 'H':
                    hlen += 1
                    j += 1
                    if j == nsyms:
                        break
                if hlen == 0:
                    frag = sym
                elif hlen == 1:
                    frag = sym + 'H'
                else:
                    frag = sym + 'H' + str(hlen)
                frag_list.append(frag)
            else:
                frag_list.append(sym)

    return frag_list        


def ratios_from_atoms(atoms):
    """Return a list of ratios for each element from the atoms.

    Parameters
    ----------
    atoms : ase.Atoms object
    """

    ct = Counter(atoms.symbols)  
    natoms = len(atoms)

    return {x: y / natoms for x, y in ct.items()}


def numbers_from_ratios(sum_numbers, ratios):
    """Return the number of atoms for each element from ratios.

    Parameters
    ----------
    sum_numbers : int
        The total number of atoms

    ratios : list
        A list of ratios for different elements
    """

    sum_ratios = sum(ratios)
    totals = [int((sum_numbers * r) // sum_ratios) for r in ratios]
    residues = [(sum_numbers * r) % sum_ratios for r in ratios]
    for i in sorted(range(len(ratios)), key=lambda i: residues[i] 
    * ratios[i], reverse=True)[:sum_numbers-sum(totals)]:
        totals[i] += 1

    return totals


def dag_from_ucg(adj_matrix, sources, return_depths=False):
    """Takes the adjacency matrix of an undirected cyclic graph
    (UCG) and the indices of the starting nodes, returns an 
    adjacency list represeting the corresponding shortest-paths 
    directed acyclic graph (DAG).

    Parameters
    ----------
    adj_matrix : np.ndarray or list of lists
        The adjacency matrix of the UCG.

    sources : list of strs
        The indices of the starting nodes for the DAG.

    return_depths : bool, default False
        Whether to also return the node indices at each walking depth 
        (in ascending order) together with the DAG.

    """

    # Get the indices of the nearest neighbors for each atom
    adj_list = [[target for target, is_connected in enumerate(row) 
                 if is_connected] for row in adj_matrix]
    sources = set(sources)
    frontier = sources.copy()
    depths = []
    dag = [[] for _ in range(len(adj_list))]

    # Iterate until no nearest neighbors can be found
    while frontier:
        if return_depths:
            depths.append(frontier)
        # Point to nearest neighbors that are not previously queried
        # Prevent pointing to nodes with same depth or backwards
        for source in frontier:            
            dag[source].extend(target for target in adj_list[source] 
                               if not target in sources)
        # Update queried atoms with new nearest neighbor set
        frontier = set(target for source in frontier for target 
                       in adj_list[source] if not target in sources)
        sources.update(frontier)

    if return_depths:
        return dag, depths

    return dag


def sort_atoms_by_ref_atoms(atoms, ref_atoms, mic=False):
    """Sort a structure based on a reference structure. This could 
    be super useful when restarting DFT relaxation in VASP since 
    VASP always shuffles the atom indices when starting a new run.
    Each pair of atoms after sorting is a closest pair. Note that
    the number of atmos of the structures must be the same. The 
    cells of the two periodic structures must be the same."""

    if mic:
        return atoms[np.asarray([find_mic(atoms.positions - 
                     np.tile(ref_atoms.positions[i], (len(atoms), 1)), 
                     cell=atoms.cell, pbc=True)[1] 
                     for i in range(len(atoms))]).argmin(1)]
    else:
        return atoms[((ref_atoms.positions[:, np.newaxis] - 
                     atoms.positions)**2).sum(2).argmin(1)]


#def relative_cosine_similarity(counter1, counter2):
#    """Computes the relative cosine similarity between two.
#    counter dictionaries (e.g. {'Pt': 5, 'Ni': 8})."""
#
#    if not counter1 and not counter2:
#        return 1
#    if not counter1 or not counter2:
#        return 0 
#
#    lenc1, lenc2 = sum(counter1.values()), sum(counter2.values())
#    lensim = min(lenc1, lenc2) / max(lenc1, lenc2)
#    terms = set(counter1).union(counter2)
#    dotprod = sum(counter1.get(k, 0) * counter2.get(k, 0) for k in terms)
#    magA = math.sqrt(sum(counter1.get(k, 0)**2 for k in terms))
#    magB = math.sqrt(sum(counter2.get(k, 0)**2 for k in terms))
#    cossim = dotprod / (magA * magB)
#
#    return lensim * cossim


def draw_graph(G, savefig='graph.png', layout='spring', *args, **kwargs):               
    """Draw the graph using matplotlib.pyplot.

    Parameters
    ----------
    G : networkx.Graph object
        The graph object

    savefig : str, default 'graph.png'
        The name of the figure to be saved.

    layout : str, default 'spring'
        The graph layout supported by networkx. E.g. 'spring',
        'graphviz', 'random', etc.

    """

    import matplotlib.pyplot as plt
    labels = nx.get_node_attributes(G, 'symbol')
    
    # Get unique groups
    groups = sorted(set(labels.values()))
    mapping = {x: "C{}".format(i) for i, x in enumerate(groups)}
    nodes = G.nodes()
    colors = [mapping[G.nodes[n]['symbol']] for n in nodes]

    # Drawing nodes, edges and labels separately
    if layout in ['graphviz', 'pygraphviz']:
        layout_to_call = getattr(nx.drawing.nx_agraph, layout + '_layout')
    else:
        layout_to_call = getattr(nx, layout + '_layout')
    pos = layout_to_call(G)
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=1.5)
    nx.draw_networkx_nodes(G, pos, 
                           nodelist=nodes, 
                           node_color=colors, 
                           node_size=500)
    nx.draw_networkx_labels(G, pos, labels, 
                            font_size=10, 
                            font_color='w')
    plt.axis('off')
    plt.savefig(savefig, *args, **kwargs)
    plt.clf()
