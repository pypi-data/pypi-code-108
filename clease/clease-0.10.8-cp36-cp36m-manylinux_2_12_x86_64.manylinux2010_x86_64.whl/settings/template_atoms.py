"""Class containing a manager for creating template atoms."""
from itertools import product
from typing import Iterator, List
from contextlib import contextmanager
import numpy as np
from numpy.random import shuffle
import ase
from ase.build.tools import niggli_reduce_cell
from ase.build import make_supercell
from clease.tools import all_integer_transform_matrices
from .template_filters import CellFilter, AtomsFilter, SkewnessFilter, EquivalentCellsFilter

__all__ = ('TemplateAtoms',)


class TemplateAtoms:

    def __init__(self, prim_cell, supercell_factor=27, size=None, skew_threshold=40, filters=()):
        if size is None and supercell_factor is None:
            raise TypeError("Either size or supercell_factor needs to be "
                            "specified.\n size: list or numpy array.\n "
                            "supercell_factor: int")

        self.supercell_factor = supercell_factor
        self._skew_threshold = skew_threshold
        self.size = size

        self.cell_filters = []
        self.atoms_filters = []

        self.add_cell_filter(SkewnessFilter(skew_threshold))

        for f in filters:
            if isinstance(f, CellFilter):
                self.add_cell_filter(f)
            elif isinstance(f, AtomsFilter):
                self.add_atoms_filter(f)

        if self.size is not None:
            self.supercell_factor = None
            check_valid_conversion_matrix(self.size)
        self.prim_cell = prim_cell

    def __eq__(self, other):
        return self.supercell_factor == other.supercell_factor and \
            self.skew_threshold == other.skew_threshold and \
            self.size == other.size and self.prim_cell == other.prim_cell

    @property
    def skew_threshold(self):
        return self._skew_threshold

    @skew_threshold.setter
    def skew_threshold(self, threshold):
        self._skew_threshold = threshold
        for f in self.cell_filters:
            if isinstance(f, SkewnessFilter):
                f.ratio = threshold

    def __str__(self):
        """Print a summary of the class."""
        msg = "=== TemplateAtoms ===\n"
        msg += f"Supercell factor: {self.supercell_factor}\n"
        msg += f"Size: {self.size}\n"
        msg += f"Skew threshold: {self.skew_threshold}\n"
        return msg

    def add_cell_filter(self, cell_filter):
        """Attach a new Cell filter."""
        if not isinstance(cell_filter, CellFilter):
            raise TypeError("filter has to be an instance of CellFilter")
        self.cell_filters.append(cell_filter)

    def add_atoms_filter(self, at_filter):
        """Attach a new Atoms filter."""
        if not isinstance(at_filter, AtomsFilter):
            raise TypeError("filter has to be an instance of AtomsFilter")
        self.atoms_filters.append(at_filter)

    def clear_filters(self):
        """Remove all filters."""
        self.cell_filters = []
        self.atoms_filters = []

    def remove_filter(self, f):
        """Remove one filter"""
        if isinstance(f, AtomsFilter):
            self.atoms_filters.remove(f)
        elif isinstance(f, CellFilter):
            self.cell_filters.remove(f)
        else:
            raise TypeError('Only AtomsFilters and CellFilters can be removed')

    def remove_filters(self, filters):
        """Remove a list of filters."""
        for f in filters:
            self.remove_filter(f)

    def is_valid(self, atoms=None, cell=None):
        """
        Check the validity of the template.

        Return `True` if templates are valid according to the attached filters.

        Parameters:

        atoms: Atoms object

        cell: unit cell vector
        """
        if atoms is None and cell is None:
            msg = "At least one of `atoms` or `cell` must be specified."
            raise ValueError(msg)

        if cell is None:
            cell = atoms.get_cell()
        cell_valid = all(f(cell) for f in self.cell_filters)

        if not cell_valid:
            return False

        atoms_valid = True
        if atoms is not None:
            atoms_valid = all(f(atoms) for f in self.atoms_filters)

        return cell_valid and atoms_valid

    def get_template_with_given_size(self, size):
        """Get the UID of the template with given size.

        Parameters:

        size: list of length 3
        """
        if not is_3x3_matrix(size):
            raise ValueError("Expect the size to be a list of 3x3 matrix")

        check_valid_conversion_matrix(size)

        template = make_supercell(self.prim_cell, size)

        if isinstance(size, np.ndarray):
            size = size.tolist()
        template.info['size'] = size

        if not self.is_valid(atoms=template):
            raise ValueError("Requested size violates the constraints!")
        return template

    def get_template_matching_atoms(self, atoms):
        """Get the UID for the template matching atoms.

        Parameters:

        atoms: Atoms object
            structure to compare its size against template atoms
        """

        size = self._get_conversion_matrix(atoms)
        assert is_3x3_matrix(size)

        prim_cell = self.prim_cell

        if isinstance(size, np.ndarray):
            size = size.tolist()

        template = make_supercell(prim_cell, size)
        template.info['size'] = size

        if not np.allclose(atoms.get_cell(), template.get_cell()):
            raise ValueError(f"Inconsistent cells! Passed atoms\n"
                             f"{atoms.get_cell()}\nGenerated template\n"
                             f"{template.get_cell()}")

        if not self.is_valid(atoms=template):
            raise ValueError("Requested template violates the constraints!")
        return template

    def _get_conversion_matrix(self, atoms):
        """Return the conversion matrix factor."""
        prim_cell = self.prim_cell

        small_cell = prim_cell.get_cell()
        inv_cell = np.linalg.inv(small_cell)

        large_cell = atoms.get_cell()
        size_factor = large_cell.dot(inv_cell)
        scale_int = size_factor.round(decimals=0).astype(int)
        if np.allclose(size_factor, scale_int):
            check_valid_conversion_matrix(scale_int)
            return scale_int.tolist()

        raise ValueError(f"The passed atoms object cannot be described by "
                         f"repeating of the unit cells. Scale factors found "
                         f"{size_factor}")

    def get_all_templates(self) -> List[ase.Atoms]:
        """Return a list with all templates."""
        return list(self.iterate_all_templates())

    def iterate_all_templates(self, max_per_size: int = None) -> Iterator[ase.Atoms]:
        """Get ass possible templates in an iterator.

        :param max_per_size: Maximum number of iterations per size.
            Optional. If None, then all sizes will be used.
        """
        if self.size is not None:
            yield self.get_template_with_given_size(self.size)
            return

        for size in range(1, self.supercell_factor):
            for ii, template in enumerate(self._iterate_templates_at_size(size)):
                # Check if we limit the number of tempaltes per size
                if max_per_size is not None and ii >= max_per_size:
                    break
                yield template

    def _iterate_templates_at_size(self, size: int) -> Iterator[ase.Atoms]:
        """Get all templates at a given size, i.e.
        a size at a given supercell factor
        """
        cells = []
        equiv_filter = EquivalentCellsFilter(cells)
        ucell = self.prim_cell.get_cell()

        matrices = all_integer_transform_matrices(size)

        for mat in matrices:
            cell = mat.dot(ucell)
            new_atoms_flag = False  # Did we create a new template?
            with self.filter_context(equiv_filter):
                if self.is_valid(cell=cell):
                    at = make_supercell(self.prim_cell, mat)
                    if self.is_valid(atoms=at):
                        at.info['size'] = mat.tolist()
                        cells.append(cell)
                        new_atoms_flag = True
            # Ensure we remove the filter again, so it does not affect the
            # global filters when processing these atoms outside
            # of this function
            if new_atoms_flag:
                yield at

    @contextmanager
    def filter_context(self, custom_filter):
        try:
            self.add_cell_filter(custom_filter)
            yield
        finally:
            self.remove_filter(custom_filter)

    def get_all_scaled_templates(self):
        """
        Return all templates that can be obtained by scaling the primitive cell
        """
        if self.size is not None:
            return [self.get_template_with_given_size(self.size)]
        cells = []
        templates = []
        equiv_filter = EquivalentCellsFilter(cells)
        self.add_cell_filter(equiv_filter)
        ucell = self.prim_cell.get_cell()
        for diag in product(range(1, self.supercell_factor + 1), repeat=3):
            if np.prod(diag) > self.supercell_factor:
                continue

            mat = np.diag(diag)
            cell = mat.dot(ucell)
            if self.is_valid(cell=cell):
                at = make_supercell(self.prim_cell, mat)
                if self.is_valid(atoms=at):
                    cells.append(cell)
                    at.info['size'] = mat.tolist()
                    templates.append(at)
        self.remove_filter(equiv_filter)
        return templates

    def weighted_random_template(self):
        """Select a random template atoms with a bias towards a cubic cell.

        The bias is towards cells that have similar values for x-, y- and
        z-dimension sizes.
        """
        if self.size is not None:
            return self.get_template_with_given_size(self.size)

        ucell = self.prim_cell.get_cell()
        max_attempts = 100000
        exp_value = self.supercell_factor**(1.0 / 3.0)
        for _ in range(max_attempts):
            diag = np.random.poisson(lam=exp_value, size=3)
            while np.prod(diag) > self.supercell_factor or np.prod(diag) == 0:
                diag = np.random.poisson(lam=exp_value, size=3)

            off_diags = np.random.poisson(lam=1, size=3)

            # Check that off diagonals are smaller or equal to diagonal
            if (off_diags[0] > diag[0] or off_diags[1] > diag[0] or off_diags[2] > diag[1]):
                continue

            matrix = np.zeros((3, 3), dtype=int)
            matrix[0, 0] = diag[0]
            matrix[1, 1] = diag[1]
            matrix[2, 2] = diag[2]
            matrix[0, 1] = off_diags[0]
            matrix[0, 2] = off_diags[1]
            matrix[1, 2] = off_diags[2]
            cell = matrix.dot(ucell)

            if self.is_valid(cell=cell):
                atoms = make_supercell(self.prim_cell, matrix)
                if self.is_valid(atoms=atoms):
                    atoms.info['size'] = matrix.tolist()
                    return atoms

        raise RuntimeError("Did not manage to generate a random template that "
                           "satisfies all the constraints")

    def has_atoms_filters(self):
        return len(self.atoms_filters) > 0

    def get_fixed_volume_templates(self, num_prim_cells=10, num_templates=10):
        # Set up a filter that listens to the templates with fixed volume
        cells = []
        transform_matrices = []

        equiv_filter = EquivalentCellsFilter(cells)
        self.add_cell_filter(equiv_filter)

        ucell = self.prim_cell.get_cell()
        matrices = list(all_integer_transform_matrices(num_prim_cells))
        shuffle(matrices)
        for mat in matrices:
            sc = mat.dot(ucell)
            sc, _ = niggli_reduce_cell(sc)
            if self.is_valid(cell=sc):
                # If Atoms filters are present we check if it is valid
                at_valid = True
                if self.has_atoms_filters():
                    atoms = make_supercell(self.prim_cell, mat)
                    at_valid = self.is_valid(atoms=atoms)
                if at_valid:
                    cells.append(sc)
                    transform_matrices.append(mat)

            if len(transform_matrices) >= num_templates:
                break

        templates = []

        if len(transform_matrices) > num_templates:
            shuffle(transform_matrices)
            transform_matrices = transform_matrices[:num_templates]

        for P in transform_matrices:
            atoms = make_supercell(self.prim_cell, P)
            templates.append(atoms)

        # Remove the filter that was artificially added
        self.cell_filters.remove(equiv_filter)
        return templates


def is_3x3_matrix(array):
    return np.array(array).shape == (3, 3)


def check_valid_conversion_matrix(array):
    """
    Make sure that we have a right-handed coordinate system.
    Raise a ValueError if the matrix is not valid.
    """
    determinant = np.linalg.det(array)
    if determinant < 0.0:
        raise ValueError(f"The determinant of the size matrix is less than "
                         f"zero (got {determinant}). For a right coordinate "
                         f"system, we need a positive determinant.")
