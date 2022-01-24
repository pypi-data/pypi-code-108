from typing import Tuple
import spglib
import numpy as np
from scipy.optimize import linear_sum_assignment
from ase.atoms import Atoms, Cell
from ase.geometry import find_mic

__all__ = ('TransformInfo', 'StructureMapper')


class TransformInfo:
    """
    Class for holding information about snap transformation
    """

    def __init__(self):
        self.displacements = []
        self.dispVec = []
        self.strain = []

    def todict(self) -> dict:
        return {'displacements': list(self.displacements), 'strain': list(self.strain)}


class StructureMapper:
    """
    Class that refines a relaxed structure to a corresponding "ideal"
    lattice.

    :param symprec: Symmetry precision (see refine_cell in spglib)
    :param angle_tol: Angle tolerance (see refine_cell in spglib)
    """

    def __init__(self, symprec: float = 0.1, angle_tol: float = 5.0):
        self.symprec = symprec
        self.angle_tol = angle_tol

    def refine(self, atoms: Atoms) -> Atoms:
        """
        Refine a relaxed atoms object. This method relies on symmetry finding.
        It handles distortions to some extent, but for heavily distorted
        systems, it will most likely fail.

        :param atoms: Relaxed atoms object
        """
        cell = np.array(atoms.get_cell())
        scaled_pos = atoms.get_scaled_positions()
        numbers = np.array(atoms.numbers)

        result = spglib.refine_cell((cell, scaled_pos, numbers),
                                    symprec=self.symprec,
                                    angle_tolerance=self.angle_tol)

        if result is None:
            raise RuntimeError("Could not refine cell")

        lattice, scaled_pos, numbers = result
        return Atoms(numbers=numbers, cell=lattice, scaled_positions=scaled_pos, pbc=[1, 1, 1])

    def strain(self, cell1: Cell, cell2: Cell) -> np.ndarray:
        """
        Calculate the strain tensor to map cell1 into cell2.
        In the following the 3x3 matrix where each cell vector is a
        column, is denoted C_1 and C_2 for cell1 and cell2, respectively.
        There is a transformation matrix P such that C_2 = PC_1. Thus,
        P = C_2C_1^{-1}. The strain tensor is defined as E = 0.5*(P^TP - I),
        where I is the identity matrix.

        :param cell1: First cell
        :param cell2: Second cell
        """
        # pylint: disable=no-self-use
        P = cell2.dot(np.linalg.inv(cell1))
        return 0.5 * (P.T.dot(P) - np.eye(3))

    def snap_to_lattice(self, atoms: Atoms, template: Atoms) -> Tuple[Atoms, TransformInfo]:
        """
        Snaps atoms to an ideal lattice. If the number of atoms in the
        relaxed atoms object is less than the number of atoms in the template,
        the method will add vacancies on sites that are not matched.

        :param atoms: Relaxed atoms object. Note that the cell and atomic
            positions will be altered.
        :param template: Ideal lattice. On return, the symbols corresponds
            to the mapped symbols in atoms
        """
        strain = self.strain(atoms.get_cell(), template.get_cell())
        atoms.set_cell(template.get_cell(), scale_atoms=True)

        # Build distance matrix using MIC
        distances = np.zeros((len(atoms), len(template)))
        cell = template.get_cell()
        all_dist_vec = []
        for atom in atoms:
            for atom_template in template:
                d = atom_template.position - atom.position
                all_dist_vec.append(d)
        distVec, micDist = find_mic(all_dist_vec, cell)
        distances = micDist.reshape((len(atoms), len(template)))

        # Snap atoms to ideal sites such that collective distance
        # is minimized
        row, assignment = linear_sum_assignment(distances)
        displacements = distances[row, assignment]
        template.numbers = np.zeros(len(template))
        template.numbers[assignment] = atoms.numbers

        transform_info = TransformInfo()
        transform_info.displacements = displacements
        transform_info.strain = strain
        transform_info.dispVec = np.array([
            distVec[i * len(template) + j] for i in range(len(atoms)) for j in range(len(template))
        ])
        return template, transform_info
