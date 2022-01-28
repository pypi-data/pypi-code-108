#! /usr/bin/env python3

"""
This is the main part of xyz_py
"""

import numpy as np
import numpy.linalg as la
from ase import neighborlist, Atoms
from ase.geometry.analysis import Analysis
import copy
import re
import scipy.optimize as spo
import sys
from collections import defaultdict
import deprecation

__version__ = "4.2.0"

# Dictionary of relative atomic masses
ram_dict = {
    "H": 1.0076,
    "He": 4.0026,
    "Li": 6.941,
    "Be": 9.0122,
    "B": 10.811,
    "C": 12.0107,
    "N": 14.0067,
    "O": 15.9994,
    "F": 18.9984,
    "Ne": 20.1797,
    "Na": 22.9897,
    "Mg": 24.305,
    "Al": 26.9815,
    "Si": 28.0855,
    "P": 30.9738,
    "S": 32.065,
    "Cl": 35.453,
    "K": 39.0983,
    "Ar": 39.948,
    "Ca": 40.078,
    "Sc": 44.9559,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938,
    "Fe": 55.845,
    "Ni": 58.6934,
    "Co": 58.9332,
    "Cu": 63.546,
    "Zn": 65.39,
    "Ga": 69.723,
    "Ge": 72.64,
    "As": 74.9216,
    "Se": 78.96,
    "Br": 79.904,
    "Kr": 83.8,
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.9059,
    "Zr": 91.224,
    "Nb": 92.9064,
    "Mo": 95.94,
    "Tc": 98,
    "Ru": 101.07,
    "Rh": 102.9055,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.411,
    "In": 114.818,
    "Sn": 118.71,
    "Sb": 121.76,
    "I": 126.9045,
    "Te": 127.6,
    "Xe": 131.293,
    "Cs": 132.9055,
    "Ba": 137.327,
    "La": 138.9055,
    "Ce": 140.116,
    "Pr": 140.9077,
    "Nd": 144.24,
    "Pm": 145,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.9253,
    "Dy": 162.5,
    "Ho": 164.9303,
    "Er": 167.259,
    "Tm": 168.9342,
    "Yb": 173.04,
    "Lu": 174.967,
    "Hf": 178.49,
    "Ta": 180.9479,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.078,
    "Au": 196.9665,
    "Hg": 200.59,
    "Tl": 204.3833,
    "Pb": 207.2,
    "Bi": 208.9804,
    "Po": 209,
    "At": 210,
    "Rn": 222,
    "Fr": 223,
    "Ra": 226,
    "Ac": 227,
    "Pa": 231.0359,
    "Th": 232.0381,
    "Np": 237,
    "U": 238.0289,
    "Am": 243,
    "Pu": 244,
    "Cm": 247,
    "Bk": 247,
    "Cf": 251,
    "Es": 252,
    "Fm": 257,
    "Md": 258,
    "No": 259,
    "Rf": 261,
    "Lr": 262,
    "Db": 262,
    "Bh": 264,
    "Sg": 266,
    "Mt": 268,
    "Rg": 272,
    "Hs": 277
}

atom_lab_num = {"H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7,
                "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13,
                "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19,
                "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25,
                "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31,
                "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37,
                "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43,
                "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49,
                "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55,
                "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61,
                "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67,
                "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72, "Ta": 73,
                "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79,
                "Hg": 80, "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85,
                "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91,
                "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97,
                "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102, "Lr": 103,
                "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108,
                "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113,
                "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118}

metals = ["Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Sc", "Ti", "V",
          "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Rb", "Sr",
          "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
          "In", "Sn", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm",
          "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf",
          "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
          "Bi", "Po", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu",
          "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf",
          "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl",
          "Mc", "Lv"]

atom_num_lab = dict(zip(atom_lab_num.values(), atom_lab_num.keys()))


def load_xyz(f_name: str, atomic_numbers: bool = False,
             add_indices: bool = False):
    """
    Load labels and coordinates from a .xyz file

    Parameters
    ----------
    f_name : str
        File name
    atomic_numbers : bool, default False
        If true, will read xyz file with atomic numbers and convert
        to labels
    add_indices : bool, default False
        If true, add indices to atomic labels
        (replacing those which may exist already)

    Returns
    -------
    list
        atomic labels
    np.ndarray
        (n_atoms,3) array containing xyz coordinates of each atom
    """

    if atomic_numbers:
        _numbers = list(np.loadtxt(f_name, skiprows=2, usecols=0, dtype=int))
        _labels = num_to_lab(_numbers)
    else:
        _labels = list(np.loadtxt(f_name, skiprows=2, usecols=0, dtype=str))

    # Set labels as capitals
    _labels = [lab.capitalize() for lab in _labels]

    if add_indices:
        _labels = remove_numbers(_labels)
        _labels = add_numbers(_labels)

    _coords = np.loadtxt(f_name, skiprows=2, usecols=(1, 2, 3))

    return _labels, _coords


def save_xyz(f_name: str, labels: list, coords: np.ndarray,
             with_numbers: bool = False, verbose: bool = True,
             mask: list = [], atomic_numbers: bool = False):
    """
    Save an xyz file containing labels and coordinates

    Parameters
    ----------
    f_name : str
        File name
    labels : list
        atomic labels
    coords : np.ndarray
        list of 3 element lists containing xyz coordinates of each atom
    with_numbers : bool, default False
        If True, add/overwrite numbers to labels before printing
    verbose : bool, default True
        Print information on filename to screen
    mask : list, optional
        n_atom list of 0 (exclude) and 1 (include) indicating which
        atoms to print
    atomic_numbers : bool, default False
        If true, will save xyz file with atomic numbers

    Returns
    -------
    None
    """

    # Option to have numbers added
    if with_numbers:
        # Remove and re-add numbers to be safe
        _labels = remove_numbers(labels)
        _labels = add_numbers(_labels)
    else:
        _labels = labels

    # Set up masks
    if mask:
        coords = np.delete(coords, mask, axis=0)
        _labels = np.delete(_labels, mask, axis=0).tolist()

    n_atoms = len(_labels)

    if atomic_numbers:
        _labels = remove_numbers(_labels)
        _numbers = lab_to_num(_labels)
        _identifier = _numbers
    else:
        _identifier = _labels

    with open(f_name, 'w') as f:
        f.write("{:d}\n\n".format(n_atoms))
        for it, (ident, trio) in enumerate(zip(_identifier, coords)):
            f.write("{:5} {:15.7f} {:15.7f} {:15.7f} \n".format(ident, *trio))

    if verbose:
        print("New xyz file written to {}".format(f_name))

    return


@deprecation.deprecated(
    deprecated_in="4.2.0", removed_in="5.1.0", current_version=__version__,
    details="Use the remove_label_indices function instead"
)
def remove_numbers(labels: list):
    """
    Remove numbers from a list of atomic labels

    Parameters
    ----------
    labels : list
        atomic labels

    Returns
    -------
    list
        atomic labels without numbers
    """

    return remove_label_indices(labels)


def remove_label_indices(labels: list):
    """
    Remove label indexing from atomic symbols
    indexing is either numbers or numbers followed by letters:
    e.g. H1, H2, H3
    or H1a, H2a, H3a

    Parameters
    ----------
    labels : list
        atomic labels

    Returns
    -------
    list
        atomic labels without indexing
    """

    labels_nn = []
    for label in labels:
        no_digits = []
        for i in label:
            if not i.isdigit():
                no_digits.append(i)
            elif i.isdigit():
                break
        result = ''.join(no_digits)
        labels_nn.append(result)

    return labels_nn


@deprecation.deprecated(
    deprecated_in="4.2.0", removed_in="5.1.0", current_version=__version__,
    details="Use the add_label_indices function instead"
)
def add_numbers(labels: list, style: str = 'per_element'):
    """
    Add numbers to a list of atomic labels

    Parameters
    ----------
    labels : list
        atomic labels
    style : str, optional
        {'per_element', 'sequential'}
            'per_element' : Number by element e.g. Dy1, Dy2, N1, N2, etc.
            'sequential' : Number the atoms 1->N regardless of element

    Returns
    -------
    list
        atomic labels with numbers
    """

    return add_label_indices(labels, style=style)


def add_label_indices(labels: list, style: str = 'per_element'):
    """
    Add label indexing to atomic symbols - either element or per atom.

    Parameters
    ----------
    labels : list
        atomic labels
    style : str, optional
        {'per_element', 'sequential'}
            'per_element' : Index by element e.g. Dy1, Dy2, N1, N2, etc.
            'sequential' : Index the atoms 1->N regardless of element

    Returns
    -------
    list
        atomic labels with indexing
    """

    # remove numbers just in case
    labels_nn = remove_numbers(labels)

    # Just number the atoms 1->N regardless of element
    if style == 'sequential':
        labels_wn = ['{}{:d}'.format(lab, it+1)
                     for (it, lab) in enumerate(labels)]

    # Index by element Dy1, Dy2, N1, N2, etc.
    if style == 'per_element':
        # Get list of unique elements
        atoms = set(labels_nn)
        # Create dict to keep track of index of current atom of each element
        atom_count = {atom: 1 for atom in atoms}
        # Create labelled list of elements
        labels_wn = []
        for lab in labels_nn:
            # Index according to dictionary
            labels_wn.append("{}{:d}".format(lab, atom_count[lab]))
            # Then add one to dictionary
            atom_count[lab] += 1

    return labels_wn


def count_n_atoms(form_str: str):
    """
    Count number of atoms in a chemical formula

    Parameters
    ----------
    form_str : str
        chemical formula string

    Returns
    -------
    int
        number of atoms in chemical formula
    """

    form_dict = formstr_to_formdict(form_str)

    n_atoms = sum(form_dict.values())

    return n_atoms


def index_elements(labels: list, shift: int = 0):
    """
    Return dictionary of element (keys) and indices (values) from list
    of labels

    Parameters
    ----------
    labels : list
        atomic labels
    shift : int, optional
        additive shift to apply to all indices

    Returns
    -------
    dict
        element (keys) and indices (values)
    """

    labels_nn = remove_numbers(labels)

    ele_index = {}

    for it, lab in enumerate(labels_nn):
        try:
            ele_index[lab].append(it+shift)
        except KeyError:
            ele_index[lab] = [it+shift]

    return ele_index


def count_elements(labels: list):
    """
    Count number of each element in a list of elements

    Parameters
    ----------
    labels : list
        atomic labels
    Returns
    -------
    dict
        dictionary of elements (keys) and counts (vals)
    """

    labels_nn = remove_numbers(labels)

    ele_count = {}

    for lab in labels_nn:
        try:
            ele_count[lab] += 1
        except KeyError:
            ele_count[lab] = 1

    return ele_count


def get_formula(labels: list):
    """
    Generates empirical formula in alphabetical order given a list of labels

    Parameters
    ----------
    labels : list
        atomic labels
    Returns
    -------
    str
        Empirical formula in alphabetical order
    """

    formdict = count_elements(labels)

    formula = formdict_to_formstr(formdict)

    return formula


def formstr_to_formdict(form_str: str):
    """
    Converts formula string into dictionary of {atomic label:quantity} pairs

    Parameters
    ----------
    form_string : str
        Chemical formula as string

    Returns
    -------
    dict
        dictionary of {atomic label:quantity} pairs
    """

    form_dict = {}
    # Thanks stack exchange!
    s = re.sub
    f = s("[()',]", '', str(eval(s(',?(\d+)', r'*\1,', s('([A-Z][a-z]*)', # noqa
          r'("\1",),', form_str))))).split()
    for c in set(f):
        form_dict[c] = f.count(c)

    return form_dict


def formdict_to_formstr(form_dict: dict, include_one: bool = False):
    """
    Converts dictionary of {atomic label:quantity} pairs into
    a single formula string in alphabetical order

    Parameters
    ----------
    form_dict : dict
        dictionary of {atomic label:quantity} pairs
    include_one : bool, default False
        Include 1 in final chemical formula e.g. C1H4

    Returns
    -------
    str
        Chemical formula as string in alphabetical order
    """

    # Formula labels and quantities as separate lists with same order
    form_labels = ["{:s}".format(key) for key in form_dict.keys()]
    form_quants = [val for val in form_dict.values()]

    # Quantities of each element as a string
    if include_one:
        form_quants_str = ["{:d}".format(quant)
                           for quant in form_quants]
    else:
        form_quants_str = ["{:d}".format(quant)
                           if quant > 1 else ""
                           for quant in form_quants]

    # Sort labels in alphabetical order
    order = np.argsort(form_labels).tolist()
    form_labels_o = [form_labels[o] for o in order]
    # Use same ordering for quantities
    form_quants_str_o = [form_quants_str[o] for o in order]

    # Make list of elementquantity strings
    form_list = [el + quant
                 for el, quant in zip(form_labels_o, form_quants_str_o)]

    # Join strings together into empirical formula
    form_string = ''.join(form_list)

    return form_string


def contains_metal(form_string: str):
    """
    Indicates if a metal is found in a chemical formula string

    Parameters
    ----------
    form_string : str
        Chemical formula as string

    Returns
    -------
    bool
        True if metal found, else False
    """
    metal_found = False

    for metal in metals:
        if metal in form_string:
            metal_found = True
            break

    return metal_found


def combine_xyz(labels_1: list, labels_2: list,
                coords_1: list, coords_2: list):
    """
    Combine two sets of labels and coordinates

    Parameters
    ----------
    labels_1 : list
        Atomic labels
    coords_1 : list
        xyz coordinates as (n_atoms, 3) array
    labels_2 : list
        Atomic labels
    coords_2 : list
        xyz coordinates as (n_atoms, 3) array

    Returns
    -------
    list
        Combined atomic labels
    np.ndarray
        Combined xyz coordinates as (n_atoms, 3) array
    """

    # Concatenate labels lists
    labels = labels_1+labels_2

    # Concatenate coordinate lists
    coords = coords_1+coords_2

    return labels, coords


def get_neighborlist(labels: list, coords: np.ndarray,
                     adjust_cutoff: dict = {}):
    """
    Calculate ASE neighbourlist based on covalent radii

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    adjust_cutoff : dict, optional
        dictionary of atoms (keys) and new cutoffs (values)

    Returns
    -------
    ASE neighbourlist object
        Neighbourlist for system
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Load molecule
    mol = Atoms("".join(labels_nn), positions=coords)

    # Define cutoffs for each atom using atomic radii
    cutoffs = neighborlist.natural_cutoffs(mol)

    # Modify cutoff if requested
    if adjust_cutoff:
        for it, label in enumerate(labels_nn):
            if label in adjust_cutoff.keys():
                cutoffs[it] = adjust_cutoff[label]

    # Create neighbourlist using cutoffs
    neigh_list = neighborlist.NeighborList(cutoffs=cutoffs,
                                           self_interaction=False,
                                           bothways=True)

    # Update this list by specifying the atomic positions
    neigh_list.update(mol)

    return neigh_list


def get_adjacency(labels: list, coords: np.ndarray, adjust_cutoff: dict = {}):
    """
    Calculate adjacency matrix using ASE based on covalent radii.

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    adjust_cutoff : dict, optional
        dictionary of atoms (keys) and new cutoffs (values)
    save : bool, default False
        If true save to file given by `f_name`
    f_name : str, default 'adjacency.dat'
        If save true, this name is used for the file containing the adjacency
        matrix

    Returns
    -------
    np.array
        Adjacency matrix with same order as labels/coords
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Get ASE neighbourlist object
    neigh_list = get_neighborlist(labels_nn, coords,
                                  adjust_cutoff=adjust_cutoff)

    # Create adjacency matrix
    adjacency = neigh_list.get_connectivity_matrix(sparse=False)

    return adjacency


def get_bonds(labels: list, coords: np.ndarray, neigh_list=None,
              verbose: bool = True, style: str = 'indices'):
    """
    Calculate list of atoms between which there is a bond.
    Using ASE. Only unique bonds are retained.
    e.g. 0-1 and not 1-0

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    neigh_list : ASE neighbourlist object, optional
        neighbourlist of system
    f_name : str, 'bonds.dat'
        filename to save bond list to
    save : bool, default False
        Save bond list to file
    verbose : bool, default True
        Print number of bonds to screen
    style : str, {'indices','labels'}
            indices : Bond list contains atom number
            labels  : Bond list contains atom label

    Returns
    -------
    list
        list of lists of unique bonds (atom pairs)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms("".join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get bonds from ASE
    # Returns: list of lists of lists containing UNIQUE bonds
    # Defined as
    # Atom 1 : [bonded atom, bonded atom], ...
    # Atom 2 : [bonded atom, bonded atom], ...
    # Atom n : [bonded atom, bonded atom], ...
    # Where only the right hand side is in the list
    is_bonded_to = ana.unique_bonds

    # Remove weird outer list wrapping the entire thing twice...
    is_bonded_to = is_bonded_to[0]
    # Create list of bonds (atom pairs) by appending lhs of above
    # definition to each element of the rhs
    bonds = []
    for it, ibt in enumerate(is_bonded_to):
        for atom in ibt:
            bonds.append([it, atom])

    # Count bonds
    n_bonds = len(bonds)

    # Set format and convert to atomic labels if requested
    if style == "labels":
        bonds = [
            [labels[atom1], labels[atom2]]
            for atom1, atom2 in bonds
        ]
    elif style == "indices":
        pass
    else:
        sys.exit("Unknown style specified")

    # Print number of bonds to screen
    if verbose:
        print('{:d}'.format(n_bonds)+' bonds')

    return bonds


def get_angles(labels: list, coords: np.ndarray, neigh_list=None,
               verbose: bool = True, style: str = 'indices'):
    """
    Calculate list of atoms between which there is a bond angle.
    Using ASE. Only unique angles are retained.
    e.g. 0-1-2 but not 2-1-0

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    neigh_list : ASE neighbourlist object, optional
        neighbourlist of system
    f_name : str, default 'angles.dat'
        filename to save angle list to
    save : bool, default False
        Save angle list to file
    verbose : bool, default True
        Print number of angles to screen
    style : str, {'indices','labels'}
            indices : Angle list contains atom number
            labels  : Angle list contains atom label

    Returns
    -------
    list
        list of lists of unique angles (atom trios)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms("".join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get angles from ASE
    # Returns: list of lists of lists containing UNIQUE angles
    # Defined as
    # Atom 1 : [[atom,atom], [atom,atom]], ...
    # Atom 2 : [[atom,atom], [atom,atom]], ...
    # Atom n : [[atom,atom], [atom,atom]], ...
    # Where only the right hand side is in the list
    is_angled_to = ana.unique_angles

    # Remove weird outer list wrapping the entire thing twice...
    is_angled_to = is_angled_to[0]
    # Create list of angles (atom trios) by appending lhs of above
    # definition to each element of the rhs
    angles = []
    for it, ibt in enumerate(is_angled_to):
        for atoms in ibt:
            angles.append([it, *atoms])

    # Count angles
    n_angles = len(angles)

    # Set format and convert to atomic labels if requested
    if style == "labels":
        angles = [
            [labels[atom1], labels[atom2], labels[atom3]]
            for atom1, atom2, atom3 in angles
        ]
    elif style == "indices":
        pass
    else:
        sys.exit("Unknown style specified")

    # Print number of angles to screen
    if verbose:
        print('{:d}'.format(n_angles)+' angles')

    return angles


def get_dihedrals(labels: list, coords: np.ndarray, neigh_list=None,
                  verbose: bool = True, style: str = 'indices'):
    """
    Calculate and list of atoms between which there is a dihedral.
    Using ASE. Only unique dihedrals are retained.
    e.g. 0-1-2-3 but not 3-2-1-0

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    neigh_list : ASE neighbourlist object, optional
        neighbourlist of system
    f_name : str, default 'dihedrals.dat'
        filename to save angle list to
    save : bool, default False
        Save angle list to file
    verbose : bool, default True
        Print number of dihedrals to screen
    style : str, {'indices','labels'}
            indices : Dihedral list contains atom number
            labels  : Dihedral list contains atom label

    Returns
    -------
    list
        list of lists of unique dihedrals (atom quads)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms("".join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get dihedrals from ASE
    # Returns: list of lists of lists containing UNIQUE dihedrals
    # Defined as
    # Atom 1 : [[atom,atom,atom], [atom,atom,atom]], ...
    # Atom 2 : [[atom,atom,atom], [atom,atom,atom]], ...
    # Atom n : [[atom,atom,atom], [atom,atom,atom]], ...
    # Where only the right hand side is in the list
    is_dihedraled_to = ana.unique_dihedrals

    # Remove weird outer list wrapping the entire thing twice...
    is_dihedraled_to = is_dihedraled_to[0]
    # Create list of dihedrals (atom quads) by appending lhs of above
    # definition to each element of the rhs
    dihedrals = []
    for it, ibt in enumerate(is_dihedraled_to):
        for atoms in ibt:
            dihedrals.append([it, *atoms])

    # Count dihedrals
    n_dihedrals = len(dihedrals)

    # Set format and convert to atomic labels if requested
    if style == "labels":
        dihedrals = [
            [
                labels[atom1],
                labels[atom2],
                labels[atom3],
                labels[atom4]
            ]
            for atom1, atom2, atom3, atom4 in dihedrals
        ]
    elif style == "indices":
        pass
    else:
        sys.exit("Unknown style specified")

    # Print number of dihedrals to screen
    if verbose:
        print('{:d}'.format(n_dihedrals)+' dihedrals')

    return dihedrals


def lab_to_num(labels: list):
    """
    Convert atomic label to atomic number

    Parameters
    ----------
    labels : list
        Atomic labels

    Returns
    -------
    list
        Atomic numbers
    """

    labels_nn = remove_numbers(labels)

    numbers = [atom_lab_num[lab] for lab in labels_nn]

    return numbers


def num_to_lab(numbers: list, numbered: bool = True):
    """
    Convert atomic number to atomic labels

    Parameters
    ----------
    numbers : list
        Atomic numbers
    numbered : bool, optional
        Add indexing number to end of atomic labels

    Returns
    -------
    list
        Atomic labels
    """

    labels = [atom_num_lab[num] for num in numbers]

    if numbered:
        labels_wn = add_numbers(labels)
    else:
        labels_wn = labels

    return labels_wn


def reflect_coords(coords: np.ndarray):
    """
    Reflect coordinates through xy plane

    Parameters
    ----------
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array

    Returns
    -------
    np.ndarray
        xyz coordinates as (n_atoms, 3) array

    """

    # Calculate normal to plane
    x = [1, 0, 0]
    y = [0, 1, 0]
    normal = np.cross(x, y)

    # Set up transformation matrix
    # https://en.wikipedia.org/wiki/Transformation_matrix#Reflection_2
    trans_mat = np.zeros([3, 3])

    trans_mat[0, 0] = 1. - 2.*normal[0]**2.
    trans_mat[1, 0] = -2.*normal[0]*normal[1]
    trans_mat[2, 0] = -2.*normal[0]*normal[2]
    trans_mat[0, 1] = -2.*normal[0]*normal[1]
    trans_mat[1, 1] = 1. - 2.*normal[1]**2.
    trans_mat[2, 1] = -2.*normal[1]*normal[2]
    trans_mat[0, 2] = -2.*normal[0]*normal[2]
    trans_mat[1, 2] = -2.*normal[1]*normal[2]
    trans_mat[2, 2] = 1. - 2.*normal[2]**2.

    # Apply operations
    coords = coords @ trans_mat

    return coords


def find_entities(labels: list, coords: np.ndarray, adjust_cutoff: dict = {}):
    """
    Finds formulae of entities given in labels and coords using adjacency
    matrix

    Parameters
    ----------
    labels : list
        atomic labels
    coords : np.ndarray
        xyz coordinates of each atom as (n_atoms, 3) array
    adjust_cutoff : dict, optional
        dictionary of atoms (keys) and new cutoffs (values) used in generating
        adjacency matrix

    Returns
    -------
    dict
        keys = molecular formula,
        vals = list of lists, where each list contains the indices of a single
                occurrence of the `key`, and the indices match the order given
                in `labels` and `coords`
    """

    # Remove label numbers if present
    _labels = remove_numbers(labels)

    # Generate adjacency matrix using ASE
    adjacency = get_adjacency(_labels, coords, adjust_cutoff=adjust_cutoff)

    # Count number of atoms
    n_atoms = len(labels)

    # Set current fragment as start atom
    curr_frag = {0}

    # List of unvisited atoms
    unvisited = set(np.arange(n_atoms))

    # Dictionary of molecular_formula:[[indices_mol1], [indices_mol2]] pairs
    mol_indices = defaultdict(list)

    # Loop over adjacency matrix and trace out bonding network
    # Make a first pass, recording in a list the atoms which are bonded to the
    # first atom.
    # Then make another pass, and record in another list all the atoms bonded
    # to those in the previous list
    # and again, and again etc.
    while unvisited:
        # Keep copy of current fragment indices to check against for changes
        prev_frag = copy.copy(curr_frag)
        for index in prev_frag:
            # Find bonded atoms and add to current fragment
            indices = list(np.nonzero(adjacency[:, index])[0])
            curr_frag.update(indices)

        # If no changes in fragment last pass, then a complete structure must
        # have been found
        if prev_frag == curr_frag:

            # Generate molecular formula of current fragment
            curr_labels = [_labels[it] for it in curr_frag]
            curr_formula = count_elements(curr_labels)

            mol_indices[formdict_to_formstr(curr_formula)].append(
                list(curr_frag)
            )

            # Remove visited atoms
            unvisited = unvisited.difference(curr_frag)

            # Reset lists of labels and indices ready for next cycle
            curr_frag = {min(unvisited)} if unvisited else curr_frag

    return dict(mol_indices)


def remove_broken(labels: list, coords: np.ndarray, formulae: list,
                  adjust_cutoff: dict = {}, verbose: bool = False,
                  save: bool = False, frag_f_name: str = "fragments.xyz",
                  clean_f_name: str = "clean.xyz",
                  mask: list = [], skip: list = []):
    """
    Deprecated, use find_entities instead.

    Parameters
    ----------
    labels : list
        list of atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    formulae : list
        list of chemical formulae stored as dictionaries with atomic
        symbol (key) count (val) pairs
    adjust_cutoff : dict, optional
        dictionary of atoms (keys) and new cutoffs (values)
    verbose : bool, optional
        print molecule count to screen
    save : bool, optional
        Save molecules and incomplete fragments to separate xyz files
    frag_f_name : str, optional
        Name for xyz file containing fragmented structures
    clean_f_name : str, optional
        Name for xyz file containing full molecules
    mask : list, optional
        list of 0 (exclude) and 1 (include) for each element
            - if used, final lists will exclude masked elements
    skip : list, optional
        List of atomic indices which shall not be visited when tracing
        bonding network

    Returns
    -------
    list
        atomic labels for full molecules
    np.ndarray
        xyz coordinates as (n_atoms, 3) array for full molecules
    list
        atomic labels for fragments
    np.ndarray
        xyz coordinates as (n_atoms, 3) array for fragments
    dict
        keys = molecular formula,
        vals = list of lists of atomic indices
                for each atom
    """

    print("xyz_py: remove_broken is deprecated, use find_entities instead")
    exit()
    return


def _calculate_rmsd(coords_1: np.ndarray, coords_2: np.ndarray):
    """
    Calculates RMSD between two structures
    RMSD = sqrt(mean(deviations**2))
    Where deviations are defined as norm([x1,y1,z1]-[x2,y2,z2])

    Parameters
    ----------
    coords_1 : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    coords_2 : np.ndarray
        xyz coordinates as (n_atoms, 3) array

    Returns
    -------
    float
        Root mean square of norms of deviation between two structures
    """

    # Check there are the same number of coordinates
    assert(len(coords_1) == len(coords_2))

    # Calculate difference between [x,y,z] of atom pairs
    diff = [trio_1 - trio_2 for trio_1, trio_2 in zip(coords_1, coords_2)]

    # Calculate square norm of difference
    norms_sq = [la.norm(trio)**2 for trio in diff]

    # Calculate mean of squared norms
    mean = np.mean(norms_sq)

    # Take square root of mean
    rmsd = np.sqrt(mean)

    return rmsd


def calculate_rmsd(coords_1: np.ndarray, coords_2: np.ndarray,
                   mask_1: list = [], mask_2: list = [], order_1: list = [],
                   order_2: list = []):
    """
    Calculates RMSD between two structures
    RMSD = sqrt(mean(deviations**2))
    Where deviations are defined as norm([x1,y1,z1]-[x2,y2,z2])
    If coords_1 and coords_2 are not the same length, then a mask array can be
    provided for either/both and is applied prior to the calculation
    coords_1 and coords_2 can also be reordered if new orders are specified
        - note this occurs BEFORE masking

    Parameters
    ----------
    coords_1 : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    coords_2 : np.ndarray
        xyz coordinates as (n_atoms, 3) array

    mask_1 : list
        list of 0 (exclude) and 1 (include) for each element in coords_1
    mask_2 : list
        list of 0 (exclude) and 1 (include) for each element in coords_2
    order_1 : list
        list of new indices for coords_1 - applied BEFORE masking
    order_2 : list
        list of new indices for coords_2 - applied BEFORE masking

    Returns
    -------
    float
        Root mean square of norms of deviation between two structures
    """

    # Set up new ordering
    if order_1:
        _order_1 = order_1
    else:
        _order_1 = range(len(coords_1))

    if order_2:
        _order_2 = order_2
    else:
        _order_2 = range(len(coords_2))

    # Apply new order
    _coords_1 = coords_1[_order_1]
    _coords_2 = coords_2[_order_2]

    # Set up masks
    if mask_1:
        _coords_1 = np.delete(_coords_1, mask_1, axis=0)

    # Set up masks
    if mask_2:
        _coords_2 = np.delete(_coords_2, mask_2, axis=0)

    # Calculate rmsd
    rmsd = _calculate_rmsd(_coords_1, _coords_2)

    return rmsd


def rotate_coords(coords: np.ndarray, alpha: float, beta: float, gamma: float):
    """
    Rotates coordinates by alpha, beta, gamma using the zyz convention
    https://easyspin.org/easyspin/documentation/eulerangles.html

    Parameters
    ----------
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    alpha : float
        alpha angle in radians
    beta : float
        beta  angle in radians
    gamma : float
        gamma angle in radians

    Returns
    -------
    np.ndarray
        xyz coordinates as (n_atoms, 3) array after rotation
        in same order as input coordinates
    """

    R = np.zeros([3, 3])

    # Build rotation matrix
    R[0, 0] = np.cos(gamma)*np.cos(beta)*np.cos(alpha) - np.sin(gamma) * np.sin(alpha) # noqa
    R[0, 1] = np.cos(gamma)*np.cos(beta)*np.sin(alpha) + np.sin(gamma) * np.cos(alpha) # noqa
    R[0, 2] = -np.cos(gamma)*np.sin(beta)
    R[1, 0] = -np.sin(gamma)*np.cos(beta)*np.cos(alpha) - np.cos(gamma) * np.sin(alpha) # noqa
    R[1, 1] = -np.sin(gamma)*np.cos(beta)*np.sin(alpha) + np.cos(gamma) * np.cos(alpha) # noqa
    R[1, 2] = np.sin(gamma)*np.sin(beta)
    R[2, 0] = np.sin(beta)*np.cos(alpha)
    R[2, 1] = np.sin(beta)*np.sin(alpha)
    R[2, 2] = np.cos(beta)

    # Create (n,3) matrix from coords list
    _coords = coords.T

    # Apply rotation matrix
    rot_coords = R @ _coords

    # Convert back to (3,n) matrix
    rot_coords = rot_coords.T

    return rot_coords


def minimise_rmsd(coords_1: np.ndarray, coords_2: np.ndarray,
                  mask_1: list = [], mask_2: list = [], order_1: list = [],
                  order_2: list = []):
    """
    Minimising the RMSD between two structures
    If coords_1 and coords_2 are not the same length, then a mask array can be
    provided for either/both and is applied prior to the calculation
    coords_1 and coords_2 can also be reordered if new orders are specified
    **note reordering occurs before masking**

    Parameters
    ----------
    coords_1 : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    coords_2 : np.ndarray
        xyz coordinates as (n_atoms, 3) array
    mask_1 : list
        list of 0 (exclude) and 1 (include) for each element in coords_1
    mask_2 : list
        list of 0 (exclude) and 1 (include) for each element in coords_2
    order_1 : list
        list of new indices for coords_1 - applied BEFORE masking
    order_2 : list
        list of new indices for coords_2 - applied BEFORE masking

    Returns
    -------
    float
        Root mean square of norms of deviation between two structures
    """

    # Set up new ordering
    if order_1:
        _order_1 = order_1
    else:
        _order_1 = range(len(coords_1))

    if order_2:
        _order_2 = order_2
    else:
        _order_2 = range(len(coords_2))

    # Apply new order
    _coords_1 = coords_1[_order_1]
    _coords_2 = coords_2[_order_2]

    # Set up masks
    if mask_1:
        _coords_1 = np.delete(_coords_1, mask_1, axis=0)

    # Set up masks
    if mask_2:
        _coords_2 = np.delete(_coords_2, mask_2, axis=0)

    # Fit alpha, beta, and gamma to minimise rmsd
    result = spo.least_squares(lambda angs: _rotate_and_rmsd(
            angs, _coords_1, _coords_2), x0=(1., 1., 1.), jac='3-point')

    # Get optimum angles
    [alpha, beta, gamma] = result.x
    rmsd = result.cost

    return rmsd, alpha, beta, gamma


def _rotate_and_rmsd(angs: list, coords_1: np.ndarray, coords_2: np.ndarray):
    """
    Rotates coords_1 by alpha, beta, gamma using the zyz convention
    https://easyspin.org/easyspin/documentation/eulerangles.html
    then calcualtes the rmsd between coords_1 and coords_2

    Parameters
    ----------
    coords_1 : np.ndarray
        xyz coordinates as (n_atoms, 3) array of first system
    coords_2 : np.ndarray
        xyz coordinates as (n_atoms, 3) array of second system
    angs : list
        alpha, beta, gamma in radians

    Returns
    -------
    np.ndarray
        xyz coordinates as (n_atoms, 3) array after rotation
        in same order as input coordinates
    """

    # Rotate coordinates of first system
    _coords_1 = rotate_coords(coords_1, angs[0], angs[1], angs[2])

    # Calculate rmsd between rotated first system and original second system
    rmsd = _calculate_rmsd(_coords_1, coords_2)

    return rmsd


def calculate_com(labels, coords):
    """
    Calculates centre-of-mass using relative atomic masses
    Parameters
    ----------
    labels : list
        list of atomic labels
    coords : np.ndarray
        xyz coordinates as (n_atoms, 3) array

    Returns
    -------
    np.ndarray
        xyz coordinates of centre of mass as (3) array
    """

    labels_nn = remove_numbers(labels)

    masses = [ram_dict[lab] for lab in labels_nn]

    com_coords = np.zeros(3)
    for trio, mass in zip(coords, masses):
        com_coords += trio * mass

    com_coords /= np.sum(masses)

    return com_coords
