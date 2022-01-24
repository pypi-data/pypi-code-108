import copy
from collections import Counter
from itertools import product
from typing import NamedTuple, Tuple, List
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
from ase.atoms import Cell
from ase import Atoms
import attr

__all__ = ('FourVector', 'construct_four_vectors')


def _int_converter(x):
    """Allow for NumPy integer types (convert to regular int)"""
    if isinstance(x, np.integer):
        return int(x)
    return x


@attr.s(frozen=True, order=True)
class FourVector:
    """Container for a vector in 4-vector space, i.e. a vector of [ix, iy, iz, sublattice].
    Represents the position of a site in terms of the number of repitions of the primitive atoms,
    as well as which sublattice it belongs to in that cell.
    """
    ix: int = attr.ib(converter=_int_converter, validator=attr.validators.instance_of(int))
    iy: int = attr.ib(converter=_int_converter, validator=attr.validators.instance_of(int))
    iz: int = attr.ib(converter=_int_converter, validator=attr.validators.instance_of(int))
    sublattice: int = attr.ib(converter=_int_converter, validator=attr.validators.instance_of(int))

    def to_cartesian(self, prim: Atoms, transposed_cell: np.ndarray = None) -> np.ndarray:
        """Convert the four vector into cartesian coordinates

        Args:
            prim (Atoms): Primitive Atoms object that defines the lattice

            transposed_cell (np.ndarray, optional): The transposed cell matrix.
             Can be passed to avoid re-calculating this property, e.g. if getting
             cartesian coordinates for multiple FourVector objects simultaniously.
             If transposed_cell is None, it is calculated from the primitive atoms object.
             Defaults to None.

        Returns:
            np.ndarray: The cartesian coordinate representation of the FourVector.
        """
        if transposed_cell is None:
            transposed_cell = prim.get_cell().T
        return np.dot(transposed_cell, self.xyz_array) + prim[self.sublattice].position

    def to_scaled(self, prim: Atoms) -> np.ndarray:
        """
        Convert the four vector into scaled coordinates

        :param prim: Primitive cell that defines the lattice
        """
        return self.xyz_array + prim.get_scaled_positions()[self.sublattice, :]

    @property
    def xyz_array(self) -> np.ndarray:
        """Return the [ix, iy, iz] component of the four-vector as a NumPy array."""
        return np.array([self.ix, self.iy, self.iz])

    def to_tuple(self) -> Tuple[int]:
        """Get the tuple representation of the four-vector
        """
        return attr.astuple(self)

    def copy(self) -> 'FourVector':
        """Create a copy of the FourVector instance."""
        return copy.copy(self)

    def shift_xyz(self, other: 'FourVector') -> 'FourVector':
        """Shift a this vector by another FourVector instance.
        Only translates the x, y, and z values, the sublattice remains the original,
        *so be mindful of the order*, i.e. a.shift_xyz(b) is not the same as b.shift_xyz(a).

        Example:

        >>> from clease.datastructures.four_vector import FourVector
        >>> a = FourVector(0, 0, 0, 0)
        >>> b = FourVector(1, 0, 0, 1)
        >>> a.shift_xyz(b)
        FourVector(ix=1, iy=0, iz=0, sublattice=0)
        >>> b.shift_xyz(a)
        FourVector(ix=1, iy=0, iz=0, sublattice=1)
        """
        if not isinstance(other, FourVector):
            raise NotImplementedError(f'Shift must be by another FourVector, got {type(other)}')

        return FourVector(self.ix + other.ix, self.iy + other.iy, self.iz + other.iz,
                          self.sublattice)


class _Box(NamedTuple):
    """
    Class defining a box. The box is defined by storing the position vector of
    the start (lower) and end (upper) of the diagonal. The names lower and upper
    refers to "lower corner" and "upper corner", respectively.
    """
    lower: np.ndarray
    upper: np.ndarray


def _supercell_is_integer_multiple(prim: Cell, supercell: Cell, tol: float = 1e-8) -> bool:
    """
    Return True ff C_{super} = C_{prim}P and P is an integer matrix. The columns of C_{super}
    is the cell vectors of the supercell and the columns of C_{prim} are the cell vectors of
    the primitive cell

    :param prim: Primitive cell
    :param supercell: Supercell
    :param tol: Tolerance for comparison
    """
    P = np.linalg.solve(prim.array.T, supercell.array.T)
    P_int = np.round(P)
    return np.max(np.abs(P - P_int)) < tol


def _make_grid(bbox: _Box, prim: Atoms) -> Tuple[List[FourVector], np.ndarray]:
    """
    Make a grid bounded by bbox using repetitions of the atomic positions in prim

    :param bbox: Bounding box for the grid
    :param prim: Primitive cell that defines the sublattice

    :return:
        four_vecs: List of FourVector of length N (where N is the number of grid
                   points)
        scaled_pos: Nx3 numpy array. Each row of scaled_pos corresponds to the
            four-vector in four_vecs
    """
    four_vecs = []
    scaled_pos = []

    ranges = [range(bbox.lower[i], bbox.upper[i] + 1) for i in range(3)] + [range(len(prim))]
    for ix, iy, iz, l in product(*ranges):
        fv = FourVector(ix, iy, iz, l)
        four_vecs.append(fv)
        scaled_pos.append(fv.to_scaled(prim))

    # Convert to 2D numpy array and perform a sanity check on the result
    scaled_pos = np.array(scaled_pos)
    assert scaled_pos.shape == (len(four_vecs), 3)
    return four_vecs, scaled_pos


def construct_four_vectors(prim: Atoms, supercell: Atoms) -> List[FourVector]:
    """
    Calculate the all four vector corresponding to the passed Atoms object. A four-vector u is
    defined by such that the position of an atom is given by C.dot(u[:3]) + prim[u[3]].position
    where the cell vectors of the primitive cell are column in the C matrix.

    The cell of the supercell must be related to the cell in prim my an integer matrix
    transformation. C_{super} = C_{prim}P. See for example `make_supercell`in ASE.

    :param prim: Primitive cell
    :param supercell: Supercell
    """
    if not _supercell_is_integer_multiple(prim.get_cell(), supercell.get_cell()):
        raise ValueError("The supercell must be an integer multiple of the primitive cell")

    if np.any(prim.get_scaled_positions() < 0.0):
        raise ValueError("Primitive cell must be wrapped")

    supercell_cpy = supercell.copy()
    supercell_cpy.set_cell(prim.get_cell())
    sc_scaled_pos = supercell_cpy.get_scaled_positions(wrap=False)

    bounding_box = _Box(lower=np.floor(np.min(sc_scaled_pos, axis=0)).astype(int),
                        upper=np.ceil(np.max(sc_scaled_pos, axis=0)).astype(int))

    # Fill the bounding box with a grid
    four_vecs_grid, scaled_pos_grid = _make_grid(bounding_box, prim)

    # Calculates pair-wise distances between the super-cell and the grid
    distances = cdist(sc_scaled_pos, scaled_pos_grid)

    # Assign exactly one atom to each grid point such that the total distance mismatch is minimize
    # (e.g. solving least linear sym assignment problem)
    _, cols = linear_sum_assignment(distances)

    # Calculate mean displacement
    four_vectors = [four_vecs_grid[c] for c in cols]

    # Sanity checks
    sub_lat_count = Counter(fv.sublattice for fv in four_vectors)

    if any(v != int(len(supercell_cpy) / len(prim)) for v in sub_lat_count.values()):
        raise RuntimeError("The four vectors are invalid as the number of atoms in each "
                           "sublattice does not match the number of primitive cells")

    if len(sub_lat_count) != len(prim):
        raise RuntimeError("The four vectors are invalid as the number of sublattice "
                           "detected does not match the number of sublattices in the "
                           "primitive cell")

    return four_vectors
