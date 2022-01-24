# pylint: disable=too-many-lines
"""A collection of miscellaneous functions used for Cluster Expansion."""
import re
import logging
from pathlib import Path
from itertools import (permutations, combinations, product, filterfalse, chain)
from collections.abc import Iterable
from typing import List, Optional, Tuple, Dict, Set, Sequence, Union
from typing import Iterable as tIterable
from typing_extensions import Protocol
import numpy as np
from numpy.random import sample, shuffle
import ase
from ase.db import connect
from ase.db.core import parse_selection
from scipy.spatial import cKDTree as KDTree
from scipy.optimize import linprog

logger = logging.getLogger(__name__)


class ApproxEqualityList:
    """
    Wrapper around a list which implements a new comparison operator. If two
    items in the list is equal within a given tolerance, the items are
    considered to be equal.

    Parameters:

    array: list
        List that is wrapped

    tol: float
        Toleracnce for comparison check
    """

    def __init__(self, array, tol=1E-5):
        self.array = array
        self.tol = tol

    def __lt__(self, other):
        for x, y in zip(self.array, other.array):
            if x - y < -self.tol:
                return True
            if x - y > self.tol:
                return False
        return False


def index_by_position(atoms):
    """Set atomic indices by its position."""
    # add zero to avoid negative zeros
    tags = atoms.get_positions() + 0
    tags = tags.tolist()
    tags = [ApproxEqualityList(x) for x in tags]
    deco = sorted([(tag, i) for i, tag in enumerate(tags)])

    indices = [i for tag, i in deco]
    return indices


def sort_by_position(atoms):
    """Sort atoms by its position."""
    # Return a new Atoms object with sorted atomic order.
    # The default is to order according to chemical symbols,
    # but if *tags* is not None, it will be used instead.
    # A stable sorting algorithm is used.
    indices = index_by_position(atoms)
    return atoms[indices]


def wrap_and_sort_by_position(atoms):
    """Wrap and sort atoms by their positions."""
    atoms.wrap()
    atoms = sort_by_position(atoms)
    return atoms


def ndarray2list(data):
    """
    Convert nested lists of a combination of lists and numpy arrays
    to list of lists
    """
    if not isinstance(data, list) and not isinstance(data, np.ndarray):
        return data

    data = list(data)
    for i, value in enumerate(data):
        data[i] = ndarray2list(value)
    return list(data)


def dec_string(deco, equiv_sites):
    """Create the decoration string based on equiv sites."""
    equiv_dec = sorted(equivalent_deco(deco, equiv_sites))
    return ''.join(str(i) for i in equiv_dec[0])


def equivalent_deco(deco, equiv_sites):
    """Generate equivalent decoration numbers based on equivalent sites."""
    if not equiv_sites:
        return [deco]

    perm = []
    for equiv in equiv_sites:
        perm.append(list(permutations(equiv)))

    equiv_deco = []
    for comb in product(*perm):
        order = []
        for item in comb:
            order += list(item)

        orig_order = list(range(len(deco)))
        for i, srt_indx in enumerate(sorted(order)):
            orig_order[srt_indx] = order[i]
        equiv_deco.append([deco[indx] for indx in orig_order])

    unique_deco = []
    for eq_dec in equiv_deco:
        if eq_dec not in unique_deco:
            unique_deco.append(eq_dec)
    return unique_deco


def flatten(x):
    """Flatten list."""
    if isinstance(x, Iterable):
        return [a for i in x for a in flatten(i)]
    return [x]


def flatten_iter(x):
    """Flatten an iterable as a generator"""
    if isinstance(x, Iterable):
        return (a for i in x for a in flatten_iter(i))
    return [x]


def nested_array2list(array):
    """Convert a nested array/tuple to a nested list."""
    if isinstance(array, np.ndarray):
        array = array.tolist()
    else:
        array = list(array)
    try:
        for i, value in enumerate(array):
            if isinstance(value, np.ndarray):
                array[i] = value.tolist()
            else:
                array[i] = list(value)
    except TypeError:
        pass
    return array


def update_db(uid_initial=None,
              final_struct=None,
              db_name=None,
              custom_kvp_init: dict = None,
              custom_kvp_final: dict = None):
    """Update the database.

    Parameters:

    uid_initial: int
        entry ID of the initial structure in the database

    final_struct: Atoms
        Atoms object with the final structure with a physical
        quantity that needs to be modeled (e.g., DFT energy)

    db_name: str
        Database name

    custom_kvp_init: dict (optional)
        If desired, one can pass additional key-value-pairs for the
        entry containing the initial structure

    custom_kvp_final: dict (optional)
        If desired, one can pass additional key-value-pairs for the
        entry containing the final structure
    """
    if custom_kvp_init is None:
        custom_kvp_init = {}
    if custom_kvp_final is None:
        custom_kvp_final = {}

    db = connect(db_name)

    init_row = db.get(id=uid_initial)

    # Check if a final structure already exits
    name = init_row.name
    select_cond = [('name', '=', name), ('struct_type', '=', 'final')]
    exist = sum(1 for row in db.select(select_cond))
    if exist >= 1:
        logger.warning("A structure with 'name'=%s and 'struct_type'=final already exits in DB.",
                       name)
        return

    # Write the final structure to database
    kvp_final = {'struct_type': 'final', 'name': name}
    kvp_final.update(custom_kvp_final)
    uid_final = db.write(final_struct, key_value_pairs=kvp_final)

    kvp_update_init = {
        'converged': True,
        'started': '',
        'queued': '',
    }
    if kvp_final['struct_type'] == 'final':
        kvp_update_init['final_struct_id'] = uid_final
    kvp_update_init.update(custom_kvp_init)

    # Update info for the initial structure
    db.update(uid_initial, **kvp_update_init)


def exclude_information_entries():
    """Return selection condition to exlcude all entries in the database that
       only contain information about the clusters.
    """
    return [('name', '!=', 'primitive_cell'), ('name', '!=', 'template')]


def get_all_internal_distances(atoms, max_dist, ref_indices):
    """Obtain all internal distances of the passed atoms object and return a
       Numpy array containing all the distances sorted in an ascending order.
    """
    tree = KDTree(atoms.get_positions())
    distances = []
    for ind in ref_indices:
        indices = tree.query_ball_point(atoms[ind].position, max_dist)
        dists = atoms.get_distances(ind, indices)
        for d in dists:
            if np.any(np.abs(np.array(distances) - d) < 1E-6):
                continue
            distances.append(d)
    distances = sorted(distances)

    # Make sure that the first element is 0
    assert distances[0] < 1E-6
    return np.array(distances[1:])


def reconfigure(settings, **kwargs) -> None:
    """Reconfigure the correlation functions for a settings object.

    Args:
        settings (ClusterExpansionSettings):
            Instance of a cluster expansion settings object.
    """
    # pylint: disable=import-outside-toplevel, cyclic-import
    from clease.corr_func import CorrFunction
    from clease.settings import ClusterExpansionSettings
    # Note, we cannot import ClusterExpansionSettings for typing,
    # otherwise we get cyclic imports.
    if not isinstance(settings, ClusterExpansionSettings):
        raise TypeError(f"settings must be of type ClusterExpansionSettings, got {type(settings)}")
    CorrFunction(settings).reconfigure_db_entries(**kwargs)


def split_dataset(X: np.ndarray,
                  y: np.ndarray,
                  nsplits: int = 10,
                  groups: Sequence[int] = ()) -> List[Dict[str, np.ndarray]]:
    """Split the dataset such that it can be used for k-fold
        cross validation.

    :param X: Design matrix
    :param y: Target values
    :param nsplits: Number of partittions
    :param groups: List of the same length as y. Each row
        in y with the same group tag, is treated as the same
        group. Datapoints in the same group are never split
        across different partitions. If an empty list is give,
        each item in y is assumed to constitute its own group.
    """
    if not groups:
        groups = list(range(len(y)))
    unique_groups = list(set(groups))

    if len(unique_groups) < nsplits:
        raise ValueError("The number of unique groups has to be greater "
                         "than the number of partitions.")
    shuffle(unique_groups)
    partitions = []
    num_validation = int(len(unique_groups) / nsplits)

    # Must at least be 1
    num_validation = max(num_validation, 1)

    for i in range(nsplits):
        start = i * num_validation
        end = (i + 1) * num_validation
        if i == nsplits - 1:
            chosen_groups = unique_groups[start:]
        else:
            chosen_groups = unique_groups[start:end]

        group_mask = np.zeros(len(groups), dtype=np.uint8)
        group_mask[chosen_groups] = 1
        index_mask = np.zeros(len(y), dtype=np.uint8)
        for j, g in enumerate(groups):
            if group_mask[g]:
                index_mask[j] = 1
        data = {
            "train_X": X[index_mask == 0, :],
            "train_y": y[index_mask == 0],
            "validate_X": X[index_mask == 1, :],
            "validate_y": y[index_mask == 1]
        }
        partitions.append(data)
    return partitions


def random_validation_set(num: int = 10,
                          select_cond: Optional[list] = None,
                          db_name: Optional[str] = None):
    """
    Construct a random test set.

    :param num: Number of datapoints to include in the test set
    :param select_cond: Select condition to be used to select items from
        the database. If not given, it will be struct_type='initial',
        converged=True
    :param db_name: Name of the database
    """
    if select_cond is None:
        select_cond = [('struct_type', '=', 'initial'), ('converged', '=', True)]

    if db_name is None:
        raise ValueError("No database provided!")

    all_ids = get_ids(select_cond, db_name)
    return sample(all_ids, num)


def exclude_ids(ids: List[int]) -> List[tuple]:
    """
    Construct a select condition based on the ids passed.

    :params ids: List of IDs
    """
    return [("id", "!=", x) for x in ids]


def symbols2integer(basis_functions):
    """Convert each symbol in the basis function
       to a unique integer.

    Parameters:

    basis_functions: list of dict
        The basis function dictionary from ClusterExpansionSettings
    """
    symb_id = {}
    for i, symb in enumerate(basis_functions[0].keys()):
        symb_id[symb] = i
    return symb_id


def bf2npyarray(basis_functions, symb_id):
    """Convert the basis function dictionary to a 2D
        numpy array

    Parameters:

    basis_function: list of dict
        Basis function dictionary from ClusterExpansionSettings

    symb_id: dict
        Dictionary of symbol integer (see symbols2integer)
    """
    bf_npy = np.zeros((len(basis_functions), len(symb_id)))

    for i, bf in enumerate(basis_functions):
        for k, v in bf.items():
            bf_npy[i, symb_id[k]] = v
    return bf_npy


def nested_list2str(nested_list):
    """Convert a nested list to string."""
    return 'x'.join(','.join(str(x) for x in item) for item in nested_list)


def str2nested_list(string):
    """Convert string to nested list."""

    def _as_int(x):
        return int(x)

    return [list(map(_as_int, item.split(','))) for item in string.split('x')]


def min_distance_from_facet(x, cell):
    """
    Calculate the minimum distance from a point to the cell facet.

    Parameters:

    x: np.array
        Position from which to calculate the minimum distance

    cell: Cell
        Cell of an Atoms object
    """
    dists = []

    for plane in combinations([0, 1, 2], r=2):
        # Unit normal vector
        n = np.cross(cell[plane[0], :], cell[plane[1], :])
        n /= np.sqrt(n.dot(n))

        # Plane with origin in it
        dist = np.abs(n.dot(x))
        dists.append(dist)

        # Opposite facet
        remaining = list(set([0, 1, 2]) - set(plane))[0]
        vec = cell[remaining, :]
        dist = np.abs(n.dot(x - vec))
        dists.append(dist)
    return min(dists)


def trans_matrix_index2tags(trans_matrix, tagged_atoms, indices=None):
    """
    Convert from indices to tags

    Parameters:

    trans_matrix: list of dict
        Original translation matrix

    tagged_atoms: Atoms
        Atoms with a tag that should be used instead of the
        index

    indices: list of int
        Atom indices corresponding to each row in trans_matrix.
        If None, it is assumed that len(trans_matrix) == len(tagged_atoms)
        and each row in trans_matrix corresponds to the atom with the same
        index in tagged_atoms.
    """
    unique_tags = sorted(list(set(atom.tag for atom in tagged_atoms)))

    if indices is None:
        indices = list(range(len(trans_matrix)))

    # Make sure we have a continuous series of tags
    assert len(unique_tags) == max(unique_tags) + 1

    new_tm = [{} for _ in range(len(unique_tags))]
    used_tags = [False for _ in range(len(unique_tags))]

    for i, row in enumerate(trans_matrix):
        tag = tagged_atoms[indices[i]].tag
        if used_tags[tag]:
            continue
        new_row = {tagged_atoms[k].tag: tagged_atoms[v].tag for k, v in row.items()}
        used_tags[tag] = True
        new_tm[tag] = new_row
    return new_tm


def indices2tags(supercell, clusters):
    for cluster in clusters:
        for i, figure in enumerate(cluster):
            cluster[i] = [int(supercell[x].tag) for x in figure]
    return clusters


def list2str(array):
    return "-".join(str(x) for x in array)


def factorize(n):
    while n > 1:
        for i in range(2, n + 1):
            if n % i == 0:
                n = int(n / i)
                yield i
                break


def count_atoms(atoms):
    """
    Return dictionary with the number of items of each species
    """
    count = {}
    for s in atoms.symbols:
        count[s] = count.get(s, 0) + 1
    return count


def all_integer_transform_matrices_given_diag(diag):
    rng1 = range(0, diag[0] + 1)
    rng2 = rng1
    rng3 = range(0, diag[1] + 1)
    for off_diag in product(rng1, rng2, rng3):
        yield np.array([[diag[0], off_diag[0], off_diag[1]], [0, diag[1], off_diag[2]],
                        [0, 0, diag[2]]])


def all_integer_transform_matrices_per_diag(n):
    """
    Yield all the integer transform matrices
    """
    diags = filterfalse(lambda x: x[0] * x[1] * x[2] != n, product(range(n + 1), repeat=3))

    for d in diags:
        yield all_integer_transform_matrices_given_diag(d)


def all_integer_transform_matrices(n):
    return chain(*all_integer_transform_matrices_per_diag(n))


def rotate_cells(cell, target_cell):
    """
    Rotate the cells such that one vector is parallel.
    And the other vector lies in a given plane
    """
    dot_prod_cell = cell.dot(cell.T)
    dot_prod_target_cell = target_cell.dot(target_cell.T)

    # Calculate unit vector cells
    uvec_cell = np.zeros_like(cell)
    uvec_target_cell = np.zeros_like(target_cell)
    for i in range(3):
        uvec_cell[i, :] = cell[i, :] / np.sqrt(dot_prod_cell[i, i])
        uvec_target_cell[i, :] = target_cell[i, :] / \
            np.sqrt(dot_prod_target_cell[i, i])

    # Rotate one vector to be parallel
    v = np.cross(uvec_cell[0, :], uvec_target_cell[0, :])
    c = uvec_cell[0, :].dot(uvec_target_cell[0, :])
    v_cross = np.zeros((3, 3))
    v[0, 1] = -v[2]
    v[0, 2] = v[1]
    v[1, 0] = v[2]
    v[1, 2] = -v[0]
    v[2, 0] = -v[1]
    v[2, 1] = v[0]
    R = np.eye(3) + v_cross + v_cross.dot(v_cross) / (1 + c)
    target_cell = R.dot(target_cell)
    return target_cell


def species_chempot2eci(bf_list, species_chempot):
    """
    Convert chemical potentials given for species to their corresponding
    singlet ECI values.

    Parameters:

    bf_list: list
        List of basis function values for each species

    species_chempot: dict
        Dictionary containing the chemical potential for each species. Note
        that the chemical potential for one species can be set to 0.0 without
        any loss of generality. Hence, the species_chempot should contain
        chemical potentials for all elements except one.
    """
    if len(species_chempot) != len(bf_list):
        msg = "Inconsistent number of chemical potentials. Basis functions\n"
        msg += f"{bf_list}. Passed chemical potentials {species_chempot}"
        raise ValueError(msg)

    n = len(species_chempot)
    mat = np.zeros((n, n))
    rhs = np.zeros(n)
    row = 0
    for sp, mu in species_chempot.items():
        for col, bf in enumerate(bf_list):
            mat[row, col] = bf[sp]
        rhs[row] = mu
        row += 1
    try:
        eci_chem_pot = np.linalg.solve(mat, rhs)
    except np.linalg.LinAlgError:
        inv_mat = np.linalg.pinv(mat)
        eci_chem_pot = inv_mat.dot(rhs)
    eci_chem_pot = eci_chem_pot.tolist()
    eci_dct = {f"c1_{i}": v for i, v in enumerate(eci_chem_pot)}
    return eci_dct


def bf2matrix(bfs):
    """
    Convert a list of basis functions to a matrix. Each column represents
    a species and each row represent a basis function.

    Parameter:

    bfs: list of dict
        List of dictionaries containing the basis function values
    """
    nrows = len(bfs)
    ncols = len(bfs[0])
    mat = np.zeros((nrows, ncols))
    keys = sorted(list(bfs[0].keys()))
    for i, bf in enumerate(bfs):
        for j, symb in enumerate(keys):
            mat[i, j] = bf[symb]
    return mat


def singlets2conc(bf_list, singlets):
    """
    Convert singlets to concentrations.

    Parameters:

    bf_list: list
        List with the basis functions (e.g [{'Au': 1, 'Cu': -1.0}])

    singlets: np.ndarray
        Array with singlets (NxM), M has to match the length of bf_list.
        The columns are assumed to given in sorted order (i.e. c1_0, c1_1,
        c1_2 etc.)
    """
    mat = bf2matrix(bf_list)

    # Add row to force that concentrations sum to 1
    mat = np.vstack((mat, np.ones(mat.shape[1])))
    singlets = np.hstack((singlets, np.ones((singlets.shape[0], 1))))

    res = np.linalg.solve(mat, singlets.T).T
    symbs = sorted(list(bf_list[0].keys()))
    concs = []
    for i in range(res.shape[0]):
        concs.append({symbs[j]: res[i, j] for j in range(res.shape[1])})
    return concs


def rate_bf_subsets(elems, bfs):
    """
    Rate different combinations of basis function according to how
    well it is able to distinguish the elements in the basis.

    Example:
    bfs = [{'Li': 1.0, 'X': 0.0, 'V': 0.0, 'F': 0.0},
           {'Li': 0.0, 'X': 1.0, 'V': 0.0, 'F': 0.0},
           {'Li': 0.0, 'X': 0.0, 'V': 1.0, 'F': 0.0}]

    If one wants basis functions for the triplet [Li, X, F] we need two
    basis functions. The following combinations are possible
    (bfs[0], bfs[1]), (bfs[0], bfs[2]), (bfs[1], bfs[2])

    The score is defined as the sum of the absolute value of the difference
    between the basis function value for the selected symbols. The score for
    the first combinations is thus

    score1 = |bfs[0]['Li'] - bfs[0]['F']| + |bfs[0]['Li'] - bfs[0]['X']| +
             |bfs[0]['F'] - bfs[0]['X']|  + |bfs[1]['Li'] - bfs[1]['F']| +
             |bfs[1]['Li'] - bfs[1]['X']| + |bfs[1]['F']  - bfs[1]['X']|

    Therefore,
    score1 = 1.0 + 1.0 + 0.0 + 0.0 + 1.0 + 1.0 = 4.0

    Parameter:

    bfs: list of dict
        List with dictionaries with the basis function values
    """
    score_and_comb = []
    for comb in combinations(range(len(bfs)), r=len(elems) - 1):
        chosen = [{s: bfs[x][s] for s in elems} for x in comb]
        mat = bf2matrix(chosen)
        score = 0.0
        for row in range(mat.shape[0]):
            for i in product(range(mat.shape[1]), repeat=2):
                score += abs(mat[row, i[0]] - mat[row, i[1]])

        score_and_comb.append((score, list(comb)))
    score_and_comb.sort(reverse=True)
    return score_and_comb


def select_bf_subsets(basis_elems, bfs):
    """
    Select a subset of basis functions that best describes the basis.
    The best subset is the one that yields the highest sum of the scores for
    each sublattice. For definition of score see docstring
    of `rate_bf_subsets`

    Parameters:

    basis_elem: nested list of strings
        Basis elements (e.g. [[Li, V], [O]])

    bfs: list of dicts
        List of dictionaries holding the basis function values
        (e.g. [{'Li' : 1.0, 'V': 0.0, 'O': 0.0},
               {'Li': 0.0, 'O': 1.0, 'V': 0.0}])
    """
    rates = []
    for elems in basis_elems:
        rates.append(rate_bf_subsets(elems, bfs))

    # Find the combination of subset selections that gives the overall highest
    # score given that a basis function can be present in only one basis
    best_selection = []
    best_score = None
    for comb in product(*rates):
        total_score = sum(rate[0] for rate in comb)
        selection = [rate[1] for rate in comb]

        # Check that no basis function is selected twice
        selected_bfs = set()
        duplicates = False
        for s in selection:
            for bf in s:
                if bf in selected_bfs:
                    duplicates = True
                else:
                    selected_bfs.add(bf)

        # Add penalty to the ones that has duplicate CF functions. This way we
        # select a combination that has the same basis function in multiple
        # atomic basis if it is possible
        if duplicates:
            total_score -= 1000.0

        if best_score is None or total_score > best_score:
            best_score = total_score
            best_selection = selection
    return best_selection


def cname_lt(cname1, cname2):
    """
    Compare two cluster names to check if the first cluster name is
    smaller than (less than, or lt) the second cluster name. Since the cluster
    names take a form 'c#_d####_#', the prefix ('c#_d####') is evaluated as a
    string while the suffix ('#') is evaluated as an integer.

    Return `True` if cname1 < cname2 and `False` otherwise.
    """
    if not isinstance(cname1, str) and isinstance(cname2, str):
        raise TypeError('cnames should be strings.')

    if cname1 in ('c0', 'c1'):
        prefix1 = cname1
    else:
        prefix1 = cname1.rpartition("_")[0]

    if cname2 in ('c0', 'c1'):
        prefix2 = cname2
    else:
        prefix2 = cname2.rpartition("_")[0]

    if prefix1 < prefix2:
        return True
    if prefix1 > prefix2:
        return False

    # Case where prefixes are the same.
    if cname1 in ('c0', 'c1'):
        suffix1 = 0
    else:
        suffix1 = int(cname1.rpartition("_")[-1])

    if cname2 in ('c0', 'c1'):
        suffix2 = 0
    else:
        suffix2 = int(cname2.rpartition("_")[-1])

    if suffix1 < suffix2:
        return True
    return False


def aic(mse, num_features, num_data_points):
    """
    Return Afaike's information criteria

    Parameters:
    mse: float
        Mean square error

    num_features: int
        Number of features in the model

    num_data_points: int
        Number of data points
    """
    return 2.0 * num_features + num_data_points * np.log(mse)


def aicc(mse, num_features, num_data_points):
    """
    Return the modified Afaike's information criterion

    Parameters:
    mse: float
        Mean square error

    num_features: int
        Number of features in the model

    num_data_points: int
        Number of data points
    """
    if num_features >= num_data_points - 1:
        denum = 1.0
    else:
        denum = num_data_points - num_features - 1
    corr = (2 * num_features**2 + 2 * num_features) / denum
    return aic(mse, num_features, num_data_points) + corr


def bic(mse, num_features, num_data_points):
    """
    Return Bayes Information Criteria

    Parameters:
    mse: float
        Mean square error

    num_features: int
        Number of features

    num_data_points: int
        Number of data points
    """
    return np.log(num_data_points) * num_features + num_data_points * np.log(mse)


def get_extension(fname: Union[str, Path]) -> str:
    """
    Return the file extension of a filename

    Parameter:

    fname: str
        Filename
    """
    return Path(fname).suffix


def add_file_extension(fname: Union[str, Path], ext: str) -> str:
    """
    Adds the wanted file extension to a filename. If a file extension
    is already present and it matches the wanted file extension, nothing
    is done. If it does not match, a ValueError is raised. Finally, if
    no file extension exist the wanted extension is added

    :param fname: file name
    :param ext: extension (with .) example (.csv, .txt, .json)
    """
    fname = Path(fname)
    current_ext = fname.suffix
    if current_ext == ext:
        return str(fname)
    if current_ext == '':
        return str(fname.with_suffix(ext))
    raise ValueError(f"Passed extenstion {current_ext} expected {ext}")


def sort_cf_names(cf_names: tIterable[str]) -> List[str]:
    """
    Return a sorted list of correlation function names. The names are
    sorted according to the following criteria

    1. Size
    2. Diameter
    3. Lexicographical order of the name itself
    """
    sizes = [int(n[1]) for n in cf_names]
    # Regular expression that extracts all digits after the occurence
    # of _d (e.g. c2_d0001_0_00 --> 0001)
    prog = re.compile("_d(\\d+)")
    dia_str = [prog.findall(n) for n in cf_names]
    dia = []
    for d in dia_str:
        if d:
            dia.append(int(d[0]))
        else:
            dia.append(0)

    sort_obj = list(zip(sizes, dia, cf_names))
    sort_obj.sort()
    return [s[-1] for s in sort_obj]


def get_ids(select_cond: List[tuple], db_name: str) -> List[int]:
    """
    Return ids in the datase that correspond to the passed selection.

    :param select_cond: ASE select conditions.

    :return: List of database IDs matching the select conditions.

    """
    keys, cmps = parse_selection(select_cond)
    db = connect(db_name)
    sql, args = db.create_select_statement(keys, cmps)

    # Extract the ids in the database that corresponds to select_cond
    sql = sql.replace('systems.*', 'systems.id')
    with connect(db_name) as db:
        con = db.connection
        cur = con.cursor()
        cur.execute(sql, args)
        ids = [row[0] for row in cur.fetchall()]
    ids.sort()
    return ids


class SQLCursor(Protocol):

    def execute(self, sql: str, placeholder: Tuple[str]) -> None:
        pass

    def fetchall(self) -> tuple:
        pass


def get_attribute(ids: List[int], cur: SQLCursor, key: str, table: str) -> list:
    """
    Retrieve the value of the given key for the rows with the given ID of
    the database entry.

    :param ids: list of IDs
    :param cur: cursor for the database
    :param key: name of the key
    :param table: name of the table
    """
    known_tables = ["text_key_values", "number_key_values"]

    if table not in known_tables:
        raise ValueError(f"Table has to be one of {known_tables}")

    sql = f'SELECT value, id FROM {table} WHERE key=?'
    id_set = set(ids)
    cur.execute(sql, (key,))

    row_id_value = {}
    for value, row_id in cur.fetchall():
        if row_id in id_set:
            row_id_value[row_id] = value

    # Convert to a list that matches the order of the IDs that
    # was passed
    return [row_id_value[k] for k in ids]


def common_cf_names(ids: Set[int], cur: SQLCursor, table: str) -> Set[str]:
    """
    Extracts all correlation function names that are present for all
    ids

    :param ids: List of ids that should be checked
    :param cur: SQL cursor
    :param table: Table to check
    """
    known_tables = ['polynomial_cf', 'binary_linear_cf', 'trigonometric_cf']
    if table not in known_tables:
        raise ValueError(f"Table has to be one of {known_tables}")

    sql = f"SELECT key, id FROM {table}"
    cur.execute(sql)
    cf_names = {}
    for cf_name, row_id in cur.fetchall():
        if row_id in ids:
            current = cf_names.get(row_id, set())
            current.add(cf_name)
            cf_names[row_id] = current

    # Calculate the intersection between all sets
    return set.intersection(*list(cf_names.values()))


def constraint_is_redundant(A_lb: np.ndarray,
                            b_lb: np.ndarray,
                            c_lb: np.ndarray,
                            d: float,
                            A_eq: np.ndarray = None,
                            b_eq: np.ndarray = None) -> bool:
    """
    The method considers the following system

    min c.dot(x) for some arbitrary c

    subject to

    A_lb.dot(x) >= b_lb
    A_eq.dot(x) = b_eq

    If the additional constraint c_lb.dot(x) >= d is redundant, the method
    returns True. The constraint specified by c_lb is redundant if the solution
    to min c_lb.dot(x) subject to the constraint above satisfies
    c_lb.dot(x) >= d. This method is know as the Linear Programming Method.

    :param A_lb: Matrix specifying the lower bounds
    :param b_lb: Vector specifying the right hand side of the lower bound
        constraint.
    :param c_lb: Vector specifying the additional in-equality constraint
    :param d: Right hand side of the additional in-equality
    :param A_eq: Matrix specifying the equality constraint. If None,
        no equality constraints exist.
    :param b_eq: Vector specifuing the right hand side of the equality
        constraints. If None, no equality constraints exist
    """
    # Scipy uses upper bounds in stead of lower bounds, convert lower bounds
    # to upper bounds by changing the sign
    res = linprog(c_lb, A_ub=-A_lb, b_ub=-b_lb, A_eq=A_eq, b_eq=b_eq)
    return c_lb @ res.x >= d


def remove_redundant_constraints(A_lb: np.ndarray,
                                 b_lb: np.ndarray,
                                 A_eq: np.ndarray = None,
                                 b_eq: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove all redundant constraints from A_lb and b_lb.

    min c.dot(x) for some arbitrary c

    subject to

    A_lb.dot(x) >= b_lb
    A_eq.dot(x) = b_eq

    :param A_lb: Matrix specifying the lower bounds
    :param b_lb: Vector specifying the right hand side of the lower bound
        constraint.
    :param A_eq: Matrix specifying the equality constraint. If None,
        no equality constraints exist.
    :param b_eq: Vector specifuing the right hand side of the equality
        constraints. If None, no equality constraints exist
    :return:
        A_lb, b_lb with only non-redundant constraints
    """
    redundant = []
    perturb = 1
    for i in range(A_lb.shape[0]):
        c_lb = A_lb[i, :]
        d = b_lb[i]

        # Make the constraint under consideration more generous by lowering the bound
        b_lb[i] -= perturb

        if constraint_is_redundant(A_lb, b_lb, c_lb, d, A_eq, b_eq):
            redundant.append(i)

        # Set the constraint back to the original value
        b_lb[i] += perturb
    return np.delete(A_lb, redundant, axis=0), np.delete(b_lb, redundant)


def remove_redundant_equations(A, b, tol=1e-6):
    R_trimmed = []
    indices = []

    Q, R = np.linalg.qr(A.T)

    k = 0
    for i in range(0, R.shape[1]):
        if abs(R[k, i]) > tol:
            R_trimmed.append(R[:, i])
            indices.append(i)
            k += 1

        if k == R.shape[0]:
            break

    R_trimmed = np.array(R_trimmed).T
    A_trimmed = Q.dot(R_trimmed).T
    return A_trimmed.copy(), b[indices]


def get_cubicness(atoms: ase.Atoms) -> float:
    """Get the 'cubicness' of an atoms object,
    the closer to 0, the more cubic the cell is."""
    cell = np.array(atoms.get_cell())
    # Normalize the cell
    cell /= atoms.get_volume()
    # Get diag of cell, and broadcast back into (3x3)
    diag = np.diag(np.diag(cell))
    # Take absolute value, as determinants can be negative.
    # We just need it to be as close to 0 as possible
    return abs(np.linalg.det(cell - diag))
