"""Module for generating new structures."""
import os
import math
import time
import logging
from copy import deepcopy
from abc import ABC

import numpy as np
from numpy.random import choice
from numpy.linalg import inv, pinv

from ase.db import connect
from ase.io.trajectory import TrajectoryReader

from clease.settings import ClusterExpansionSettings
from clease.corr_func import CorrFunction
from clease.tools import wrap_and_sort_by_position
from clease.calculator import Clease
from clease.montecarlo import Montecarlo, TooFewElementsError
from clease.montecarlo.observers import LowestEnergyStructure, Snapshot
from clease.montecarlo.constraints import ConstrainSwapByBasis

logger = logging.getLogger(__name__)

__all__ = ('StructureGenerator', 'GSStructure', 'MetropolisTrajectory', 'ProbeStructure')


# pylint: disable=too-many-instance-attributes
class StructureGenerator(ABC):
    """Base class for generating new strctures."""

    def __init__(self,
                 settings,
                 atoms,
                 init_temp=None,
                 final_temp=None,
                 num_temp=5,
                 num_steps_per_temp=10000):
        if not isinstance(settings, ClusterExpansionSettings):
            raise TypeError(f"Settings must be a ClusterExpansionSettings object, got {settings}")

        self.settings = settings
        self.trans_matrix = settings.trans_matrix
        self.cf_names = self.settings.all_cf_names
        self.corrFunc = CorrFunction(settings)
        self.cfm = self._get_full_cf_matrix()
        self.atoms = wrap_and_sort_by_position(atoms.copy())
        self.settings.set_active_template(atoms=self.atoms)
        if self._is_valid(atoms):
            if len(atoms) != len(settings.atoms):
                raise ValueError("Passed Atoms has a wrong size.")
        else:
            raise ValueError("concentration of the elements in the provided"
                             " atoms is not consistent with the settings.")

        # eci set to 1 to ensure that all correlation functions are included
        # but the energy produced from this should never be used
        self.eci = {name: 1. for name in self.cf_names}
        calc = Clease(self.settings, eci=self.eci)
        self.atoms.calc = calc
        self.output_every = 30
        self.init_temp = init_temp
        self.final_temp = final_temp
        self.temp = self.init_temp
        self.num_temp = num_temp
        self.num_steps_per_temp = num_steps_per_temp
        self.alter_composition = True

        # Structures and correlation function associated with
        # the generated structure so far
        self.generated_structure = None
        self.cf_generated_structure = None

    def _is_valid(self, atoms):
        return self.settings.concentration.is_valid(self.settings.index_by_basis, atoms)

    def _reset(self):
        pass

    def generate(self):
        """Generate new structures."""
        # Start
        self._reset()
        if self.init_temp is None or self.final_temp is None:
            self.init_temp, self.final_temp = self._determine_temps()

        if self.init_temp <= self.final_temp:
            raise ValueError("Initial temperature must be higher than final temperature")
        self._reset()

        temps = np.logspace(math.log10(self.init_temp), math.log10(self.final_temp), self.num_temp)
        now = time.time()
        change_element = self._has_more_than_one_conc()

        N = len(temps)
        # Number of integers for max counters
        len_num_steps = len(str(self.num_steps_per_temp))
        len_max_temp = len(str(N))
        logger.info("Generating log statements every %s s", self.output_every)

        for Ti, temp in enumerate(temps):
            self.temp = temp
            num_accepted = 0
            count = 0
            while count < self.num_steps_per_temp:
                count += 1

                if time.time() - now > self.output_every:
                    acc_rate = float(num_accepted) / count
                    msg = (
                        f"T Step: {Ti+1:>{len_max_temp}} of {N}, "
                        # Print same len as max required
                        f"Temp: {temp:>10.3f}, "
                        # Print same len as max required
                        f"MC Step: {count:>{len_num_steps}d} of "
                        f"{self.num_steps_per_temp}, "
                        f"Accept. rate: {acc_rate*100:.2f} %")
                    logger.info(msg)
                    now = time.time()

                if choice([True, False]) and self.alter_composition:
                    logger.debug('Change element type? %s', change_element)
                    # Change element Type
                    if change_element:
                        self._change_element_type()
                    else:
                        continue
                else:
                    indx = self._swap_two_atoms()
                    logger.debug('Swapping indices %s', indx)
                    if self.atoms[indx[0]].symbol == \
                            self.atoms[indx[1]].symbol:
                        logger.debug('Same symbols detected, skipping.')
                        continue
                self.atoms.get_potential_energy()

                if self._accept():
                    num_accepted += 1
                    self.atoms.calc.clear_history()
                else:
                    self.atoms.calc.restore()

        # Create a new calculator and attach it to the generated structure
        calc = Clease(self.settings, eci=self.eci, init_cf=self.cf_generated_structure)
        self.generated_structure.calc = calc

        # Force an energy evaluation to update the results dictionary
        self.generated_structure.get_potential_energy()

        # Check that correlation function match the expected value
        self._check_consistency()
        cf = self.corrFunc.get_cf(self.generated_structure)
        return self.generated_structure, cf

    def _set_generated_structure(self):
        self.generated_structure = self.atoms.copy()
        cf_dict = self.atoms.calc.get_cf()
        self.cf_generated_structure = deepcopy(cf_dict)

    def _accept(self) -> bool:
        """Determine if we accept the last change."""
        # pylint: disable=no-self-use
        return True

    def _estimate_temp_range(self):
        # pylint: disable=no-self-use
        return 1.0, 1e5

    def _determine_temps(self):
        logger.info("Temperature range not given. Determining the range automatically.")
        self._reset()
        count = 0
        max_count = 100
        now = time.time()
        # To avoid errors, just set the temperature to an arbitrary file
        self.temp = 10000000.0
        while count < max_count:
            if time.time() - now > self.output_every:
                logger.info("Progress (%.3f %%)", 100 * count / max_count)
                now = time.time()

            if choice([True, False]) and self.alter_composition:
                # Change element Type
                if self._has_more_than_one_conc():
                    self._change_element_type()
                    count += 1
                else:
                    continue
            else:
                indx = self._swap_two_atoms()
                if self.atoms[indx[0]].symbol == \
                        self.atoms[indx[1]].symbol:
                    continue
                count += 1
            self.atoms.get_potential_energy()

            # By calling accept statistics on the correlation
            # function and variance will be collected
            self._accept()
        init_temp, final_temp = self._estimate_temp_range()
        self.temp = init_temp
        logger.info("init_temp=%s, final_temp=%s", init_temp, final_temp)
        return init_temp, final_temp

    def _swap_two_atoms(self):
        """Swap two randomly chosen atoms."""
        indx = np.zeros(2, dtype=int)
        symbol = [None] * 2

        basis_elements = self.settings.basis_elements
        num_basis = self.settings.num_basis

        # pick fist atom and determine its symbol and type
        while True:
            basis = choice(range(num_basis))
            # a basis with only 1 type of element should not be chosen
            if len(basis_elements[basis]) < 2:
                continue
            indx[0] = choice(self.settings.index_by_basis[basis])
            symbol[0] = self.atoms[indx[0]].symbol
            break
        # pick second atom that occupies the same basis.
        while True:
            indx[1] = choice(self.settings.index_by_basis[basis])
            symbol[1] = self.atoms[indx[1]].symbol
            if symbol[1] in basis_elements[basis]:
                break

        # Swap two elements
        self.atoms[indx[0]].symbol = symbol[1]
        self.atoms[indx[1]].symbol = symbol[0]

        return indx

    def _has_more_than_one_conc(self):
        ranges = self.settings.concentration.get_individual_comp_range()
        for r in ranges:
            if abs(r[1] - r[0]) > 0.01:
                return True
        return False

    def _change_element_type(self):
        """Change the type of element for the atom with a given index.

        If index and replacing element types are not specified, they are
        randomly generated.
        """
        basis_elements = self.settings.basis_elements
        num_basis = self.settings.num_basis
        # ------------------------------------------------------
        # Change the type of element for a given index if given.
        # If index not given, pick a random index
        # ------------------------------------------------------
        while True:
            basis = choice(range(num_basis))
            # a basis with only 1 type of element should not be chosen
            if len(basis_elements[basis]) < 2:
                continue

            indx = choice(self.settings.index_by_basis[basis])
            old_symbol = self.atoms[indx].symbol

            # change element type
            new_symbol = choice(basis_elements[basis])
            if new_symbol != old_symbol:
                self.atoms[indx].symbol = new_symbol

                if self.settings.concentration.is_valid(self.settings.index_by_basis, self.atoms):
                    break
                self.atoms[indx].symbol = old_symbol

    def _check_consistency(self):
        # Check to see if the cf is indeed preserved
        final_cf = \
            self.corrFunc.get_cf_by_names(
                self.generated_structure,
                self.atoms.calc.cf_names)
        for k in final_cf:
            if abs(final_cf[k] - self.cf_generated_structure[k]) > 1E-6:
                msg = 'Correlation function changed after simulated annealing'
                logger.error(msg)

                # Print a summary of all basis functions (useful for debuggin)
                logger.debug('Basis functions:')
                for k2 in final_cf:
                    logger.debug('   %s: %s, %s', k2, final_cf[k2], self.cf_generated_structure[k2])
                raise ValueError(msg)

    def _get_full_cf_matrix(self):
        """Get correlation function of every entry in DB."""
        cfm = []
        db = connect(self.settings.db_name)
        tab_name = f"{self.settings.basis_func_type.name}_cf"
        for row in db.select(struct_type='initial'):
            cfm.append([row[tab_name][x] for x in self.cf_names])
        cfm = np.array(cfm, dtype=float)
        return cfm


class ProbeStructure(StructureGenerator):
    """Generate probe structures.

    Based on simulated annealing according to the recipe in
    PRB 80, 165122 (2009).

    Parameters:

    settings: CEBulk or BulkSapcegroup object

    atoms: Atoms object
        initial structure to start the simulated annealing

    init_temp: int or float
        initial temperature (does not represent *physical* temperature)

    final_temp: int or float
        final temperature (does not represent *physical* temperature)

    num_temp: int
        number of temperatures to be used in simulated annealing

    num_steps_per_temp: int
        number of steps per temperature in simulated annealing

    approx_mean_var: bool
        whether or not to use a spherical and isotropical distribution
        approximation scheme for determining the mean variance.
        -'True': Assume a spherical and isotropical distribution of
                 structures in the configurational space.
                 Corresponds to eq.4 in PRB 80, 165122 (2009)
        -'False': Use sigma and mu of eq.3 in PRB 80, 165122 (2009)
                  to characterize the distribution of structures in
                  population.
                  Requires pre-sampling of random structures before
                  generating probe structures.
                  Reads sigma and mu from 'probe_structure-sigma_mu.npz' file.
    """

    def __init__(self,
                 settings,
                 atoms,
                 init_temp=None,
                 final_temp=None,
                 num_temp=5,
                 num_steps_per_temp=1000,
                 approx_mean_var=False):

        StructureGenerator.__init__(self, settings, atoms, init_temp, final_temp, num_temp,
                                    num_steps_per_temp)
        self.o_cf = self.atoms.calc.cf
        self.o_cfm = np.vstack((self.cfm, self.o_cf))
        self.approx_mean_var = approx_mean_var
        fname = 'probe_structure-sigma_mu.npz'
        if not approx_mean_var:
            if os.path.isfile(fname):
                data = np.load(fname)
                self.sigma = data['sigma']
                self.mu = data['mu']
                self.o_mv = mean_variance(self.o_cfm, self.sigma, self.mu)
            else:
                raise IOError(f"'{fname}' not found.")
        else:
            self.o_mv = mean_variance_approx(self.o_cfm)
        self.avg_mv = 0.0
        self.num_steps = 0
        self.avg_diff = 0.0

        self.min_mv = None

    def _accept(self):
        """Accept the last change."""
        cfm = np.vstack((self.cfm, self.atoms.calc.cf))
        if self.approx_mean_var:
            n_mv = mean_variance_approx(cfm)
        else:
            n_mv = mean_variance(cfm, self.sigma, self.mu)

        # Always accept the first move
        if self.generated_structure is None:
            self.min_mv = n_mv
            self._set_generated_structure()
            return True

        if n_mv < self.o_mv:
            self.min_mv = n_mv
            self._set_generated_structure()

        if self.o_mv > n_mv:
            accept = True
        else:
            accept = np.exp((self.o_mv - n_mv) / self.temp) > np.random.uniform()

        self.avg_diff += abs(n_mv - self.o_mv)
        if accept:
            self.o_mv = n_mv

        self.avg_mv += self.o_mv
        self.num_steps += 1
        return accept

    def _estimate_temp_range(self):
        if self.num_steps == 0:
            return 100000.0, 1.0
        avg_diff = self.avg_diff / self.num_steps
        init_temp = 10 * avg_diff
        final_temp = 0.01 * avg_diff
        return init_temp, final_temp

    @property
    def avg_mean_variance(self):
        if self.num_steps == 0:
            return 0.0
        return self.avg_mv / self.num_steps

    def _reset(self):
        self.avg_mv = 0.0
        self.avg_diff = 0.0
        self.num_steps = 0


class GSStructure(StructureGenerator):
    """Generate ground-state structure.

    Parameters:

    settings: CEBulk or BulkSapcegroup object

    atoms: Atoms object
        initial structure to start the simulated annealing

    init_temp: int or float
        initial temperature (does not represent *physical* temperature)

    final_temp: int or float
        final temperature (does not represent *physical* temperature)

    num_temp: int
        number of temperatures to be used in simulated annealing

    num_steps_per_temp: int
        number of steps per temperature in simulated annealing

    eci: dict
        Dictionary containing cluster names and their ECI values
    """

    def __init__(self,
                 settings,
                 atoms,
                 init_temp=2000,
                 final_temp=10,
                 num_temp=10,
                 num_steps_per_temp=100000,
                 eci=None):
        StructureGenerator.__init__(self, settings, atoms, init_temp, final_temp, num_temp,
                                    num_steps_per_temp)
        self.alter_composition = False
        self.eci = eci
        calc = Clease(self.settings, eci=eci)
        self.atoms.calc = calc

    def generate(self):
        low_en_obs = LowestEnergyStructure(self.atoms, verbose=False)
        cnst = ConstrainSwapByBasis(self.atoms, self.settings.index_by_basis)

        temps = np.logspace(math.log10(self.init_temp), math.log10(self.final_temp), self.num_temp)
        try:
            for T in temps.tolist():
                logger.info("Current temperature: %.3f K", T)
                mc = Montecarlo(self.atoms, T)
                mc.attach(low_en_obs)
                mc.generator.add_constraint(cnst)
                mc.run(steps=self.num_steps_per_temp)
            self.generated_structure = low_en_obs.emin_atoms
        except TooFewElementsError:
            # In case there are two few elements, the ground state is equal to
            # the initial configuration
            self.generated_structure = self.atoms

        cf = self.corrFunc.get_cf(self.generated_structure)
        # cf_trimmed = {key: value for (key, value) in cf
        #               if key in list(self.eci.keys())}
        calc = Clease(self.settings, eci=self.eci)
        self.generated_structure.calc = calc
        self.generated_structure.get_potential_energy()

        return self.generated_structure, cf


class MetropolisTrajectory:

    def __init__(self, settings, atoms, num):
        self.settings = settings
        self.atoms = atoms
        self.num = num

    def generate(self):
        cnst = ConstrainSwapByBasis(self.atoms, self.settings.index_by_basis)
        eci = {'c0': 0.0}
        calc = Clease(self.settings, eci=eci)
        self.atoms.calc = calc

        mc = Montecarlo(self.atoms, 10000000)
        mc.generator.add_constraint(cnst)
        fname = 'metropolis_traj'
        obs = Snapshot(self.atoms, fname=fname)
        mc.attach(obs, interval=1)

        mc.run(steps=self.num)

        reader = TrajectoryReader(obs.fname)
        all_atoms = list(reader)
        reader.close()
        obs.close()
        os.remove(obs.fname)
        return all_atoms


def mean_variance_full(cfm):
    prec = precision_matrix(cfm)
    mv = 0.
    for x in range(cfm.shape[0]):
        mv += cfm[x].dot(prec).dot(cfm[x].T)
    mv = mv / cfm.shape[0]
    return mv


def mean_variance(cfm, sigma, mu):
    prec = precision_matrix(cfm)
    return np.trace(prec.dot(sigma)) + mu.dot(prec).dot(mu.T)


def mean_variance_approx(cfm):
    prec = precision_matrix(cfm)
    return np.trace(prec)


def precision_matrix(cfm):
    try:
        prec = inv(cfm.T.dot(cfm))
    # if inverting matrix leads to a singular matrix, reduce the matrix
    except np.linalg.linalg.LinAlgError:
        prec = pinv(cfm.T.dot(cfm))
    return prec
