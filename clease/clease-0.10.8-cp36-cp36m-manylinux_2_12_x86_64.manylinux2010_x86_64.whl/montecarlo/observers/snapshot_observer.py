from typing import Sequence
from ase.atoms import Atoms
from ase.io.trajectory import TrajectoryWriter
from clease.datastructures import SystemChange
from clease.tools import add_file_extension
from .mc_observer import MCObserver


class Snapshot(MCObserver):
    """Store a snapshot in a trajectory file.

    :param atoms: Instance of the atoms objected modofied by the MC object
    :param fname: Name of the trajectory file. Adds extension '.traj' if none is given.
    :param mode: IO mode used by the ASE TrajectoryWriter (must be w or a)
    """

    name = "Snapshot"

    def __init__(self, atoms: Atoms, fname: str = "snapshot.traj", mode: str = "w"):
        super().__init__()
        full_fname = add_file_extension(fname, '.traj')
        self.atoms = atoms
        self.traj = TrajectoryWriter(full_fname, mode=mode)
        self.fname = full_fname

    def __call__(self, system_changes: Sequence[SystemChange]):
        """Write a snapshot to a .traj file.

        Parameters:

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """
        self.traj.write(self.atoms)

    def close(self):
        """Close the trajectory file."""
        self.traj.close()
