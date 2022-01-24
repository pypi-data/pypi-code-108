"""Calculator for Cluster Expansion."""
import sys
import contextlib
from typing import Dict, Optional, TextIO, Union, List
import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator
from clease_cxx import PyCEUpdater
from clease.datastructures import SystemChange, SystemChanges
from clease.corr_func import CorrFunction
from clease.settings import ClusterExpansionSettings


class MovedIgnoredAtomError(Exception):
    """Raised when ignored atoms is moved."""


class KeepChanges:

    def __init__(self):
        self.keep_changes = True


# pylint: disable=too-many-instance-attributes
class Clease(Calculator):
    """Class for calculating energy using CLEASE.

    :param settings: `ClusterExpansionSettings` object

    :param eci: Dictionary containing cluster names and their ECI values

    :param init_cf: (Optional) One can supply the correlation function values
        of the Atoms object to skip the initial assessment step. The dictionary
        should contain cluster names (same as the ones provided in `eci`) and
        their correlation function values.

    :logfile: One can pass the file object or string of the file name to get a
        log file. Do not specify or set it to *None* to avoid generating a log
        file. Use '-' for stdout.
    """

    name = 'CLEASE'
    implemented_properties = ['energy']

    def __init__(self,
                 settings: ClusterExpansionSettings,
                 eci: Dict[str, float],
                 init_cf: Optional[Dict[str, float]] = None,
                 logfile: Union[TextIO, str, None] = None) -> None:
        Calculator.__init__(self)

        if not isinstance(settings, ClusterExpansionSettings):
            msg = "settings must be CEBulk or CECrystal object."
            raise TypeError(msg)
        self.parameters["eci"] = eci
        self.settings = settings
        self.corrFunc = CorrFunction(settings)
        self.eci = eci
        # store cluster names
        self.cf_names = list(eci.keys())

        # calculate init_cf or convert init_cf to array
        if init_cf is None or isinstance(init_cf, dict):
            self.init_cf = init_cf
        else:
            msg = "'init_cf' must be a dictionary containing cluster names "
            msg += "and their correlation function values."
            raise TypeError(msg)

        if self.init_cf is not None and len(self.eci) != len(self.init_cf):
            msg = "length of provided ECIs and correlation functions do not "
            msg += "match"
            raise ValueError(msg)

        # logfile
        if isinstance(logfile, str):
            if logfile == '-':
                logfile = sys.stdout
            else:
                # pylint: disable=consider-using-with
                logfile = open(logfile, 'a')
        self.logfile = logfile

        # reference atoms for calculating the cf and energy for new atoms
        self.atoms = None
        self.symmetry_group = None
        self.is_backround_index = None

        # C++ updater initialized when atoms are set
        self.updater = None

    def _set_norm_factors(self) -> None:
        """Set normalization factor for each cluster.

        The normalization factor only kicks in when the cell is too small and
        thus, include self-interactions. This methods corrects the impact of
        self-interactions.
        """
        symm_group = np.zeros(len(self.settings.atoms), dtype=np.uint8)
        for num, group in enumerate(self.settings.index_by_sublattice):
            symm_group[group] = num

        cluster_list = self.settings.cluster_list
        for cluster in cluster_list:
            fig_keys = list(set(cluster.get_all_figure_keys()))
            num_occ = {}
            for key in fig_keys:
                num_occ[key] = cluster_list.num_occ_figure(key, cluster.name, symm_group,
                                                           self.settings.trans_matrix)
            num_fig_occ = cluster.num_fig_occurences
            norm_factors = {}
            for key in fig_keys:
                tot_num = num_occ[key]
                num_unique = len(set(key.split("-")))
                norm_factors[key] = \
                    float(tot_num)/(num_unique*num_fig_occ[key])

            norm_factor_list = []
            for fig in cluster.indices:
                key = cluster.get_figure_key(fig)
                norm_factor_list.append(norm_factors[key])
            cluster.info['normalization_factor'] = norm_factor_list

    def set_atoms(self, atoms: Atoms) -> None:
        self.atoms = atoms

        if self.init_cf is None:
            self.init_cf = \
                self.corrFunc.get_cf_by_names(self.atoms, self.cf_names)

        if len(self.settings.atoms) != len(atoms):
            msg = "Passed Atoms object and settings.atoms should have same "
            msg += "number of atoms."
            raise ValueError(msg)

        if not np.allclose(atoms.positions, self.settings.atoms.positions):
            msg = "Positions of all atoms in the passed Atoms object and "
            msg += "settings.atoms should be the same. "
            raise ValueError(msg)

        self.symmetry_group = np.zeros(len(atoms), dtype=int)
        for symm, indices in enumerate(self.settings.index_by_sublattice):
            self.symmetry_group[indices] = symm
        self.is_backround_index = np.zeros(len(atoms), dtype=np.uint8)
        self.is_backround_index[self.settings.background_indices] = 1

        self._set_norm_factors()
        self.updater = PyCEUpdater(self.atoms, self.settings, self.init_cf, self.eci,
                                   self.settings.cluster_list)

    def get_energy_given_change(self, system_changes: SystemChanges, keep_changes=False) -> float:
        """
        Calculate the energy when the change is known. No checking will be
        performed.

        :param system_changes: List of system changes. For example, if the
            occupation of the atomic index 23 is changed from Mg to Al,
            system_change = [(23, Mg, Al)]. If an Mg atom occupying the atomic
            index 26 is swapped with an Al atom occupying the atomic index 12,
            system_change = [(26, Mg, Al), (12, Al, Mg)]
        :param keep_changes: Should the calculator revert to the state prior to
            the system changes, or should the calculator stay in the new state
            with the given system changes. Default: False
        """
        with self.with_system_changes(system_changes) as keeper:
            keeper.keep_changes = keep_changes
            return self.energy

    def check_state(self, atoms: Atoms, tol: float = 1e-15):
        res = super().check_state(atoms)
        syst_ch = self.indices_of_changed_atoms

        if syst_ch and 'energy' not in res:
            res.append('energy')
        return res

    def reset(self):
        self.results = {}

    # pylint: disable=signature-differs
    def calculate(self, atoms: Atoms, properties: Union[List[str], str],
                  system_changes: SystemChanges) -> float:
        """Calculate the energy of the passed Atoms object.

        If accept=True, the most recently used atoms object is used as a
        reference structure to calculate the energy of the passed atoms.
        Returns energy.

        :param atoms: ASE Atoms object

        :param properties: List of what needs to be calculated.
            It can only by 'energy' at the moment.

        :param system_changes: List of system changes. For example, if the
            occupation of the atomic index 23 is changed from Mg to Al,
            system_change = [(23, Mg, Al)]. If an Mg atom occupying the atomic
            index 26 is swapped with an Al atom occupying the atomic index 12,
            system_change = [(26, Mg, Al), (12, Al, Mg)]
        """
        self.update_energy()
        self.energy = self.updater.get_energy()
        return self.energy

    def clear_history(self) -> None:
        self.updater.clear_history()

    def restore(self) -> None:
        """Restore the Atoms object to its original configuration and energy.

        This method reverts the Atoms object to its oldest state stored in
        memory. The state is restored to either
        (1) an initial state when the calculator was attached, or
        (2) the state at which the `clear_history()` method was invoked last
            time.

        NOTE: The maximum capacity for the history buffer is 1000 steps
        """
        self.updater.undo_changes()
        self.energy = self.updater.get_energy()

    def update_energy(self) -> None:
        """Update correlation function and get new energy."""
        self.update_cf()
        self.energy = self.updater.get_energy()

    @property
    def energy(self):
        return self.results.get('energy', None)

    @energy.setter
    def energy(self, value):
        self.results['energy'] = value

    @property
    def indices_of_changed_atoms(self) -> List[int]:
        """Return the indices of atoms that have been changed."""
        changed = self.updater.get_changed_sites(self.atoms)
        for index in changed:
            if self.is_backround_index[index] and \
                    not self.settings.include_background_atoms:
                msg = f"Atom with index {index} is a background atom."
                raise MovedIgnoredAtomError(msg)

        return changed

    def get_cf(self) -> Dict[str, float]:
        """Return the correlation functions as a dict"""
        return self.updater.get_cf()

    def update_cf(self, system_changes: SystemChanges = None) -> None:
        """Update correlation function based on the reference value.

        :param system_changes: List of system changes. For example, if the
            occupation of the atomic index 23 is changed from Mg to Al,
            system_change = [(23, Mg, Al)]. If an Mg atom occupying the atomic
            index 26 is swapped with an Al atom occupying the atomic index 12,
            system_change = [(26, Mg, Al), (12, Al, Mg)]
            If system_changes is None, the correlation functions are recalculated.
            Default: None.
        """
        if system_changes is None:
            swapped_indices = self.indices_of_changed_atoms
            symbols = self.updater.get_symbols()
            system_changes = [
                SystemChange(index=idx,
                             old_symb=symbols[idx],
                             new_symb=self.atoms[idx].symbol,
                             name='internal_symbol_change') for idx in swapped_indices
            ]
        for change in system_changes:
            self.updater.update_cf(change)

    @property
    def cf(self) -> List[float]:
        temp_cf = self.updater.get_cf()
        return [temp_cf[x] for x in self.cf_names]

    def log(self) -> None:
        """Write energy to log file."""
        if self.logfile is None:
            return
        self.logfile.write(f"{self.energy}\n")
        self.logfile.flush()

    def update_eci(self, eci: Dict[str, float]) -> None:
        """Update the ECI values.

        :param eci: dictionary with new ECI values
        """
        self.eci = eci
        self.updater.set_eci(eci)
        self._on_eci_changed()

    def get_singlets(self) -> np.ndarray:
        return self.updater.get_singlets()

    def get_energy(self) -> float:
        self.energy = self.updater.get_energy()
        return self.energy

    def _on_eci_changed(self):
        """
        Callback that is called after ECIs are changed. It is provided such
        that calculators inheriting from this class (and implementing this
        method) can be notified when the ECIs are changed.
        """

    @contextlib.contextmanager
    def with_system_changes(self, system_changes: SystemChanges):
        """
        : param system_changes: List of system changes. For example, if the
            occupation of the atomic index 23 is changed from Mg to Al,
            system_change = [(23, Mg, Al)]. If an Mg atom occupying the atomic
            index 26 is swapped with an Al atom occupying the atomic index 12,
            system_change = [(26, Mg, Al), (12, Al, Mg)]
        """
        keeper = KeepChanges()  # We need an object we can mutate to flag for cleanup
        try:
            # Apply the updates
            self.apply_system_changes(system_changes)
            yield keeper
        finally:
            if keeper.keep_changes:
                # Keep changes
                self.keep_system_changes()
            else:
                # Revert changes
                self.undo_system_changes()

    def apply_system_changes(self, system_changes: SystemChanges) -> None:
        """Apply a set of changes to the calculator, and evaluate the energy"""
        self.reset()
        # Apply the updates
        self.update_cf(system_changes)
        self.energy = self.updater.get_energy()

    def undo_system_changes(self) -> None:
        """Revert a set of changes. The changes passed in should be the original
        sequence of system changes which were applied. Restores the original results."""
        self.restore()  # Also restores results

    def keep_system_changes(self) -> None:
        """A set of system changes are to be kept. Perform necessary actions to prepare
        for a new evaluation."""
        self.clear_history()
