"""This module defines the "Figure" class, which is a collection of FourVector objects."""
from typing import Iterable, Any, Tuple
import attr
import ase
import numpy as np
from .four_vector import FourVector

__all__ = ('Figure',)


def _convert_figure(x: Any) -> Any:
    """Perform a possible type conversion on the input, prior to validation.
    We allow any iterable, which can be converted into a tuple.
    No duplication checks are made."""
    # Fast-track the tuple case, since this is the correct type of the class
    # and it is also an Iterable.
    if not isinstance(x, tuple) and isinstance(x, Iterable):
        # Try to convert into a tuple
        x = tuple(x)
    return x


@attr.s(frozen=True, order=False)
class Figure:
    """Class which defines a Figure, i.e. a collection of FourVector objects
    which defines a single cluster. Each entry in the components must be a FourVector,
    and is checked upon construction. The order of the FourVector objects is preserved,
    and is not checked for duplicate entries.

    It is possible to pass in the FourVectors in any Iterable, which will be then
    converted into a tuple, e.g.

    >>> from clease.datastructures import Figure, FourVector
    >>> fv1 = FourVector(0, 0, 0, 0)
    >>> fv2 = FourVector(1, 1, 1, 1)
    >>> Figure([fv1, fv2])
    >>> Figure((fv1, fv2))
    """

    components: Tuple[FourVector] = attr.ib(converter=_convert_figure,
                                            validator=attr.validators.instance_of(tuple))

    @components.validator
    def _validate_all_four_vectors(self, attribute, value):
        """Perform a check that all elements in the components sequence are FourVector objects"""
        # pylint: disable=unused-argument, no-self-use
        # The signature of this function is dictated by attrs.
        for ii, v in enumerate(value):
            if not isinstance(v, FourVector):
                raise TypeError(f'All values must FourVector type, got {value} '
                                f'of type {type(v)} in index {ii}.')

    def to_cartesian(self, prim: ase.Atoms, transposed_cell: np.ndarray = None) -> np.ndarray:
        """Get the Figure in terms of the cartesian coordinates, as defined
        by the primitive lattice.

        Args:
            prim (ase.Atoms): The primitive atoms cell, which defines the lattice.
            transposed_cell (np.ndarray, optional): Optional pre-calculated transposed
             cell of the primitive.

        Returns:
            np.ndarray: The cartesian coordinates of the Figure.
        """
        if transposed_cell is None:
            transposed_cell = prim.get_cell().T

        cart = np.zeros((self.size, 3))
        for ii, fv in enumerate(self.components):
            cart[ii, :] = fv.to_cartesian(prim, transposed_cell=transposed_cell)
        return cart

    def get_diameter(self, prim: ase.Atoms, transposed_cell: np.ndarray = None) -> float:
        """Calculate the diameter of the figure, as the maximum distance to the
        geometric center of the figure in cartesian coordinates.

        Args:
            prim (ase.Atoms): The primitive atoms cell, which defines the lattice.
            transposed_cell (np.ndarray, optional): Optional pre-calculated transposed
             cell of the primitive.

        Returns:
            float: The diameter of Figure.
        """

        X = self.to_cartesian(prim, transposed_cell=transposed_cell)
        # Center at the geometric center
        X -= np.mean(X, axis=0)
        # Convert to distances
        dists = np.linalg.norm(X, axis=1, ord=2)
        # Find the maximum distance (radius), and convert to diameter
        return float(2 * dists.max())

    @property
    def size(self) -> int:
        """Size of this cluster, i.e. the number of FourVector components."""
        return len(self.components)
