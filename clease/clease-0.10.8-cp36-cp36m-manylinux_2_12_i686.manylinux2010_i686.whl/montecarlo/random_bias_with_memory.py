import numpy as np
from .bias_potential import BiasPotential


class RandomBiasWithMemory(BiasPotential):
    """
    Adds a random normal distributed correction to each structure.
    Visited structures are remembered, such that a consistent correction is
    added to the structures

    Parameters:

    std: float
        Standard deviation of the correction in eV

    atoms: Atoms
        Atoms object used for the Monte Carlo sampling
    """

    def __init__(self, std, atoms):
        BiasPotential.__init__(self)
        self.std = std
        self.atoms = atoms
        self.history = {}

    def get_hash_key(self):
        """
        Return an integer hash corresponding to the current structure
        """
        return hash(tuple(self.atoms.numbers))

    def __call__(self, sytem_changes):
        """
        This method is called by the sampler after the changes of the trial
        move has been inserted. Thus, self.atoms is already updated at the
        time this function is called by the sampler.
        """
        hash_key = self.get_hash_key()
        value = self.history.get(hash_key, np.random.normal(scale=self.std))
        self.history[hash_key] = value
        return value

    def calculate_from_scratch(self, atoms):
        self.atoms.numbers = atoms.numbers
        return self(None)
