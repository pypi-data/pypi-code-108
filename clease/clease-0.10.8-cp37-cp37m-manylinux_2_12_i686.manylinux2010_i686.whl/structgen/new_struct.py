"""Module for generating new structures for training."""
import os
from copy import deepcopy
from functools import reduce
from typing import List, Dict, Optional, Union
import logging
from itertools import product

import numpy as np
from numpy.random import shuffle

from ase import Atoms
from ase.io import read
from ase.db import connect
from ase.utils.structure_comparator import SymmetryEquivalenceCheck
from ase.io.trajectory import TrajectoryReader

from clease import db_util
from clease.settings import ClusterExpansionSettings
from clease.corr_func import CorrFunction

from clease.montecarlo import TooFewElementsError
from clease.tools import wrap_and_sort_by_position, nested_list2str
from clease.tools import count_atoms
from .structure_generator import (ProbeStructure, GSStructure, MetropolisTrajectory)

try:
    from math import gcd
except ImportError:
    from fractions import gcd

logger = logging.getLogger(__name__)

max_attempt = 10
max_fail = 10

__all__ = ('NewStructures', 'MaxAttemptReachedError')


class NotValidTemplateException(Exception):
    """The template did not yield a valid atoms object"""


class MaxAttemptReachedError(Exception):
    """Raised when number of try reaches 10."""


class NewStructures:
    """
    Generate new structure in ASE Atoms object format.

    :param settings: Cluster expansion settings.

    :param generation_number: Generation number to be assigned to the newly
        generated structure

    :param struct_per_gen: Number of structures to generate per generation
    """

    def __init__(self,
                 settings: ClusterExpansionSettings,
                 generation_number: int = None,
                 struct_per_gen: int = 5) -> None:
        self.settings = settings
        self.db = connect(settings.db_name)
        self.corrfunc = CorrFunction(self.settings)
        self.struct_per_gen = struct_per_gen

        if generation_number is None:
            self.gen = self._determine_gen_number()
        else:
            self.gen = generation_number

    def num_in_gen(self) -> int:
        with connect(self.settings.db_name) as db:
            cur = db.connection.cursor()
            cur.execute("SELECT id FROM number_key_values WHERE key=? AND value=?",
                        ("gen", self.gen))
            num_in_gen = len(cur.fetchall())
        return num_in_gen

    def num_to_gen(self) -> int:
        return max(self.struct_per_gen - self.num_in_gen(), 0)

    def generate_probe_structure(self,
                                 atoms: Optional[Atoms] = None,
                                 init_temp: Optional[float] = None,
                                 final_temp: Optional[float] = None,
                                 num_temp: int = 5,
                                 num_steps_per_temp: int = 1000,
                                 approx_mean_var: bool = True,
                                 num_samples_var: int = 10000) -> None:
        """
        Generate a probe structure according to PRB 80, 165122 (2009).

        :param atoms: ASE Atoms object with the desired cell size and shape of
            the new structure.
        :param init_temp: initial temperature (does not represent *physical*
            temperature)
        :param final_temp: final temperature (does not represent *physical*
            temperature)
        :param num_temp: number of temperatures to be used in simulated
            annealing
        :param num_steps_per_temp: number of steps in simulated annealing
        :param approx_mean_var: whether or not to use a spherical and
            isotropical distribution approximation scheme for determining the
            mean variance.

            -`True`: Assume a spherical and isotropical distribution of
                structures in the configurational space. Corresponds to eq.4
                in PRB 80, 165122 (2009)
            -`False`: Use sigma and mu of eq.3 in PRB 80, 165122 (2009)
                to characterize the distribution of structures in population.
                Requires pre-sampling of random structures before generating
                probe structures. sigma and mu are generated and stored in
                'probe_structure-sigma_mu.npz' file.
        :param num_samples_var: number of samples to be used in determining
            signam and mu. Only used when `approx_mean_var` is `True`.

        Note: init_temp and final_temp are automatically generated if either
              one of the two is not specified.
        """

        if not approx_mean_var:
            # check to see if there are files containing mu and sigma values
            if not os.path.isfile('probe_structure-sigma_mu.npz'):
                self._generate_sigma_mu(num_samples_var)

        logger.info(("Generate %s probe structures (generation: %s, "
                     "struct_per_gen=%s, %s present)"), self.num_to_gen(), self.gen,
                    self.struct_per_gen, self.num_in_gen())

        current_count = 0
        num_attempt = 0
        num_to_generate = self.num_to_gen()

        while current_count < num_to_generate:
            self.settings.set_active_template(atoms=atoms)
            # Break out of the loop if reached struct_per_gen
            num_struct = self.num_in_gen()
            if num_struct >= self.struct_per_gen:
                break

            struct = self._get_struct_at_conc(conc_type='random')

            logger.info("Generating structure %s out of %s.", current_count + 1, num_to_generate)
            ps = ProbeStructure(self.settings, struct, init_temp, final_temp, num_temp,
                                num_steps_per_temp, approx_mean_var)
            probe_struct, cf = ps.generate()

            # Remove energy from result dictionary
            probe_struct.calc.results.pop('energy')
            formula_unit = self._get_formula_unit(probe_struct)
            if self._exists_in_db(probe_struct, formula_unit):
                msg = "generated structure is already in DB.\n"
                msg += "generating again... "
                msg += f"{num_attempt + 1} out of {max_attempt} attempts."
                logger.info(msg)
                num_attempt += 1
                if num_attempt >= max_attempt:
                    msg = "Could not generate probe structure in "
                    msg += f"{max_attempt} attempts."
                    logger.error(msg)
                    raise MaxAttemptReachedError(msg)
            else:
                num_attempt = 0

            logger.info("Probe structure generated.")
            self.insert_structure(init_struct=probe_struct, cf=cf)
            current_count += 1

    @property
    def corr_func_table_name(self) -> str:
        return f"{self.settings.basis_func_type.name}_cf"

    def generate_gs_structure_multiple_templates(self,
                                                 eci: Dict[str, float],
                                                 num_templates: int = 20,
                                                 num_prim_cells: int = 2,
                                                 init_temp: float = 2000.0,
                                                 final_temp: float = 1.0,
                                                 num_temp: int = 10,
                                                 num_steps_per_temp: int = 1000) -> None:
        """
        Generate ground-state structures using multiple templates
        (rather than using fixed cell size and shape). Structures are generated
        until the number of structures with the current `generation_number` in
        database reaches `struct_per_gen`.

        :param num_templates: Number of templates to search in. Simmulated
            annealing is done in each cell and the one with the lowest energy
            is taken as the ground state.
        :param num_prim_cells: Number of primitive cells to use when
            constructing templates. The volume of all the templates used will
            be num_prim_cells*vol_primitive, where vol_primitive is the volume
            of the primitive cell.

        See docstring of `generate_gs_structure` for the rest of the arguments.
        """

        for i in range(self.num_to_gen()):
            logger.info("Generating ground-state structures: %s of %s", i, self.struct_per_gen)

            self._generate_one_gs_structure_multiple_templates(
                eci=eci,
                num_templates=num_templates,
                num_prim_cells=num_prim_cells,
                init_temp=init_temp,
                final_temp=final_temp,
                num_temp=num_temp,
                num_steps_per_temp=num_steps_per_temp)

    def _generate_one_gs_structure_multiple_templates(self,
                                                      eci: Dict[str, float],
                                                      num_templates: int = 20,
                                                      num_prim_cells: int = 2,
                                                      init_temp: float = 2000.0,
                                                      final_temp: float = 1.0,
                                                      num_temp: int = 10,
                                                      num_steps_per_temp=1000) -> None:
        """
        Generate one ground-state structures using multiple templates
        (rather than using fixed cell size and shape).

        :param num_templates: Number of templates to search in. Simmulated
            annealing is done in each cell and the one with the lowest energy
            is taken as the ground state.
        :param num_prim_cells: Number of primitive cells to use when
            constructing templates. The volume of all the templates used will
            be num_prim_cells*vol_primitive, where vol_primitive is the volume
            of the primitive cell.

        See docstring of `generate_gs_structure` for the rest of the arguments.
        """
        templates = self.settings.template_atoms.get_fixed_volume_templates(
            num_templates=num_templates, num_prim_cells=num_prim_cells)

        if len(templates) == 0:
            msg = "Could not find any templates with matching the constraints"
            raise RuntimeError(msg)

        self.settings.set_active_template(atoms=templates[0])

        nib = [len(x) for x in self.settings.index_by_basis]
        x = self.settings.concentration.get_random_concentration(nib=nib)
        num_insert = self.settings.concentration.conc_in_int(nib, x)

        energies = []
        gs_structs = []
        cf_dicts = []
        for i, atoms in enumerate(templates):
            logger.info("Searching for GS in template %d of %d", i, len(templates))
            self.settings.set_active_template(atoms=atoms)

            struct = self._random_struct_at_conc(num_insert)
            es = GSStructure(self.settings, struct, init_temp, final_temp, num_temp,
                             num_steps_per_temp, eci)

            gs_struct, cf_struct = es.generate()
            gs_structs.append(gs_struct)
            cf_dicts.append(cf_struct)
            energies.append(gs_struct.get_potential_energy())

        # Find the position of the minimum energy structure
        min_energy_indx = np.argmin(energies)
        gs = gs_structs[min_energy_indx]
        cf = cf_dicts[min_energy_indx]

        self.settings.set_active_template(atoms=gs)
        self.insert_structure(init_struct=gs, cf=cf)

    def generate_gs_structure(self,
                              atoms: Union[Atoms, List[Atoms]],
                              eci: Dict[str, float],
                              init_temp: float = 2000.0,
                              final_temp: float = 1.0,
                              num_temp: int = 10,
                              num_steps_per_temp: int = 1000,
                              random_composition: bool = False) -> None:
        """
        Generate ground-state structures based on cell sizes and shapes of the
        passed ASE Atoms.

        :param atoms: Atoms object with the desired size and composition of
            the new structure. A list of Atoms with different size and/or
            compositions can be passed. Compositions of the supplied Atoms
            object(s) are ignored when random_composition=True.
        :param eci: cluster names and their ECI values
        :param init_temp: Initial temperature (does not represent *physical*
            temperature)
        :param final_temp: Final temperature (does not represent *physical*
            temperature)
        :param num_temp: Number of temperatures to use in simulated annealing
        :param num_steps_per_temp: Number of steps in simulated annealing
        :param random_composition: Whether or not to fix the composition of the
            generated structure.

            1. *False* and atoms = Atoms object: One ground-state structure with
                matching size and composition of the supplied Atoms object is
                generated
            2. *False* and atoms = list: The same number of ground-state
                structures that matches the length of the list is generated

                * Note 1: num_struct_per_gen is ignored and all of the generated
                    structures have the same generation number
                * Note 2: each GS structure will have matching size and
                    composition of the suplied Atoms objects
            3. *True* and atoms = Atoms object: GS structure(s) with a
                matching size of the Atoms object is generated at a random
                composition (within the composition range specified in
                Concentration class)

                * Note 1: This will generate GS structures until the number of
                    structures with the current generation number equals
                    num_struct_per_gen
                * Note 2: A check is performed to ensure that none of the newly
                    generated GS structures have the same composition
            4. *True* and atoms = list: The same number of GS structures that
                matches the length of the list is generated

                * Note 1: num_struct_per_gen is ignored and all of the generated
                        structures have the same generation number
                * Note 2: each GS structure will have matching sizes of the
                        supplied Atoms objects but with a random composition
                * Note 3: No check is performed to ensure that all new GS
                        structures have unique composition
        """
        structs = self._set_initial_structures(atoms, random_composition)
        current_count = 0
        num_attempt = 0
        num_to_generate = min([self.num_to_gen(), len(structs)])
        while current_count < num_to_generate:
            struct = structs[current_count].copy()
            self.settings.set_active_template(atoms=struct)
            logger.info("Generating structure %d out of %d.", current_count + 1, num_to_generate)
            es = GSStructure(self.settings, struct, init_temp, final_temp, num_temp,
                             num_steps_per_temp, eci)
            gs_struct, cf = es.generate()
            formula_unit = self._get_formula_unit(gs_struct)

            if self._exists_in_db(gs_struct, formula_unit):
                msg = "generated structure is already in DB.\n"
                msg += "generating again... "
                msg += f"{num_attempt + 1} out of {max_attempt} attempts"
                logger.info(msg)
                num_attempt += 1
                if num_attempt >= max_attempt:
                    msg = f'Could not generate ground-state structure in {max_attempt} attempts.'
                    logger.error(msg)
                    raise MaxAttemptReachedError(msg)
                continue

            num_attempt = 0

            min_energy = gs_struct.get_potential_energy()
            logger.info("Structure with E = %.3f generated.", min_energy)
            self.insert_structure(init_struct=gs_struct, cf=cf)
            current_count += 1

    def generate_random_structures(self, atoms: Optional[Atoms] = None) -> None:
        """
        Generate random structures until the number of structures with
        `generation_number` equals `struct_per_gen`.

        :param atoms: If Atoms object is passed, the passed object will be
            used as a template for all the random structures being generated.
            If None, a random template will be chosen.
            (different for each structure)
        """
        logger.info(
            ("Generating %d random structures (generation: %s, struct_per_gen=%d, %d present)."),
            self.num_to_gen(), self.gen, self.struct_per_gen, self.num_in_gen())

        fail_counter = 0
        i = 0

        num_structs = self.num_to_gen()
        while i < num_structs and fail_counter < max_fail:
            if self.generate_one_random_structure(atoms=atoms):
                i += 1
                fail_counter = 0
                logger.debug("Generated %d random structures", i)
            else:
                fail_counter += 1
                logger.debug("Failed generating structure. Fail count: %d", fail_counter)

        if fail_counter >= max_fail:
            msg = ("Could not find a structure that does not exist in DB after "
                   f"{int(max_attempt * max_fail)} attempts.")
            logger.error(msg)
            raise MaxAttemptReachedError(msg)
        logger.info('Succesfully generated %d random structures.', self.num_in_gen())

    def generate_one_random_structure(self, atoms: Optional[Atoms] = None) -> bool:
        """
        Generate and insert a random structure to database if a unique
        structure is found.

        Returns ``True`` if unique structure is found and inserted in DB,
        ``False`` otherwise.

        :param atoms: If Atoms object is passed, the passed object will be
            used as a template for all the random structures being generated.
            If None, a random template will be chosen.
            (different for each structure)
        """
        num_attempts = 0
        unique_structure_found = False

        while not unique_structure_found and num_attempts < max_attempt:
            self.settings.set_active_template(atoms=atoms)
            new_atoms = self._get_struct_at_conc(conc_type="random")
            fu = self._get_formula_unit(new_atoms)
            if not self._exists_in_db(new_atoms, fu):
                unique_structure_found = True
            else:
                num_attempts += 1

        if not unique_structure_found:
            logger.warning(("Could not find a structure that does not already exist "
                            "in the DB within %d attempts."), max_attempt)
            return False

        logger.debug('Found unique structure after %d attempts.', num_attempts)
        self.insert_structure(init_struct=new_atoms)
        return True

    # pylint: disable=too-many-branches
    def _set_initial_structures(self,
                                atoms: Union[Atoms, List[Atoms]],
                                random_composition: bool = False) -> List[Atoms]:
        structs = []
        if isinstance(atoms, Atoms):
            struct = wrap_and_sort_by_position(atoms)
            if random_composition is False:
                num_to_gen = 1
                logger.debug("Generate 1 ground-state structure.")
                structs.append(struct)
            else:
                msg = f"Generate {self.num_to_gen()} ground-state structures"
                msg += f"(generation: {self.gen}, "
                msg += f"struct_per_gen={self.struct_per_gen}, "
                msg += f"{self.num_in_gen()} present)"
                logger.info(msg)
                self.settings.set_active_template(atoms=struct)
                num_to_gen = self.num_to_gen()
                concs = []
                # Get unique concentrations
                num_attempt = 0
                nib = [len(x) for x in self.settings.index_by_basis]
                while len(concs) < num_to_gen:
                    x = self.settings.concentration.get_random_concentration(nib=nib)
                    if True in [np.allclose(x, i) for i in concs]:
                        num_attempt += 1
                    else:
                        concs.append(x)
                        num_attempt = 0

                    if num_attempt > 100:
                        msg = f"Could not find {self.num_to_gen} unique "
                        msg += "compositions using the provided Atoms object."
                        raise RuntimeError(msg)
                num_atoms_in_basis = [len(indices) for indices in self.settings.index_by_basis]
                for x in concs:
                    num_insert = self.settings.concentration.conc_in_int(num_atoms_in_basis, x)
                    structs.append(self._random_struct_at_conc(num_insert))

        else:
            # This is a list of atoms objects
            logger.info("Generating %d ground-state structures.", len(atoms))
            if random_composition is False:
                for struct in atoms:
                    structs.append(wrap_and_sort_by_position(struct))
            else:
                concs = []
                nib = [len(x) for x in self.settings.index_by_basis]
                for struct in atoms:
                    self.settings.set_active_template(atoms=struct)
                    x = self.settings.concentration.get_random_concentration(nib=nib)
                    num_atoms_in_basis = [len(indices) for indices in self.settings.index_by_basis]
                    num_insert = self.settings.concentration.conc_in_int(num_atoms_in_basis, x)
                    structs.append(self._random_struct_at_conc(num_insert))
        return structs

    def generate_initial_pool(self, atoms: Optional[Atoms] = None) -> None:
        """
        Generate initial pool of structures.

        Initial pool of structures are generated, in sequence, using

        1. generate_conc_extrema(): structures at concentration where the
           number of consituting elements is at its max/min.
        2. generate_random_structures(): random structures are random
           concentration.

        Structures are genereated until the number of structures reaches
        `struct_per_gen`.

        :param atoms: If Atoms object is passed, the size and shape of its
                      cell will be used for all the random structures.
                      If None, a randome size and shape will be chosen for
                      each structure.
        """

        self.generate_conc_extrema()
        self.generate_random_structures(atoms=atoms)

    def generate_conc_extrema(self) -> None:
        """Generate initial pool of structures with max/min concentration."""
        logger.info(("Generating one structure per concentration where the number "
                     "of an element is at max/min"))
        indx_in_each_basis = []
        start = 0
        for basis in self.settings.concentration.basis_elements:
            indx_in_each_basis.append(list(range(start, start + len(basis))))
            start += len(basis)

        for indx in product(*indx_in_each_basis):
            # We only iterate 1 template per size, as any other template with the same size
            # would only be able to accomodate the same concentrations,
            # so we need to increase the size anyway in case of an error.
            for template in self.settings.template_atoms.iterate_all_templates(max_per_size=1):
                self.settings.set_active_template(template)
                try:
                    atoms = self._get_struct_at_conc(conc_type="max", index=indx)
                except NotValidTemplateException:
                    continue
                atoms = wrap_and_sort_by_position(atoms)
                self.insert_structure(init_struct=atoms)
                break
            else:
                raise RuntimeError(f'Did not find a valid template for index {indx}')

    def generate_metropolis_trajectory(self,
                                       atoms: Optional[Atoms] = None,
                                       random_comp: bool = True) -> None:
        """
        Generate a set of structures consists of single atom swaps

        :param atoms: ASE Atoms object that will be used as a template for the
            trajectory
        :param random_comp: If 'True' the passed atoms object will be
            initialised with a random composition. Otherwise, the trajectory
            will start from the passed Atoms object.
        """
        if atoms is None:
            atoms = self.settings.atoms.copy()

        if random_comp:
            self.settings.set_active_template(atoms=atoms)
            atoms = self._get_struct_at_conc(conc_type="random")

        num = self.num_to_gen()
        try:
            generator = MetropolisTrajectory(self.settings, atoms, num)
            all_atoms = generator.generate()
            for a in all_atoms:
                self.insert_structure(init_struct=a)

        except TooFewElementsError as exc:
            if random_comp:
                self.generate_metropolis_trajectory(atoms=atoms, random_comp=True)
            else:
                raise exc

    def _get_struct_at_conc(self, conc_type: str = 'random', index: int = 0) -> Atoms:
        """Generate a structure at a concentration specified.

        :param conc_type: One of 'min', 'max' and 'random'
        :param index: Index of the flattened basis_element array to specify
            which element to be maximized/minimized
        """
        conc = self.settings.concentration
        if conc_type == 'min':
            x = conc.get_conc_min_component(index)
        elif conc_type == 'max':
            x = conc.get_conc_max_component(index)
        else:
            nib = [len(x) for x in self.settings.index_by_basis]
            x = conc.get_random_concentration(nib=nib)

        num_atoms_in_basis = [len(indices) for indices in self.settings.index_by_basis]
        num_to_insert = conc.conc_in_int(num_atoms_in_basis, x)
        atoms = self._random_struct_at_conc(num_to_insert)

        if conc_type in ['min', 'max']:
            # Check how close we got, and see if we got to an acceptable range
            new_conc = conc.get_concentration_vector(self.settings.index_by_basis, atoms)
            # check if we're close enough
            # TODO: Allow a tolerance here
            if not np.allclose(new_conc, x):
                raise NotValidTemplateException(('Did not find an atoms with a '
                                                 'satisfactory concentration.'))

        return atoms

    def insert_structures(self,
                          traj_init: str,
                          traj_final: Optional[str] = None,
                          cb=lambda num, tot: None) -> None:
        """
        Insert a sequence of initial and final structures from their
        trajectory files.

        :param traj_init: Name of a trajectory file with initial structures
        :param traj_final: Name of a trajectory file with the final structures
        :param cb: Callback function that is called every time a structure is
            inserted (or rejected because it exists before). The signature of
            the function is cb(num, tot) where num is the number of inserted
            structure and tot is the total number of structures that should
            be inserted
        """
        traj_in = TrajectoryReader(traj_init)

        if traj_final is None:
            for i, init in enumerate(traj_in):
                self.insert_structure(init_struct=init)
                cb(i + 1, len(traj_in))
            return

        traj_final = TrajectoryReader(traj_final)

        if len(traj_in) != len(traj_final):
            raise ValueError("Different number of structures in "
                             "initial trajectory file and final.")

        num_ins = 0
        for init, final in zip(traj_in, traj_final):
            # Check that composition (except vacancies matches)
            count_init = count_atoms(init)
            count_final = count_atoms(final)
            for key, value in count_final.items():
                if key not in count_init:
                    raise ValueError("Final and initial structure contains " "different elements")

                if count_init[key] != value:
                    raise ValueError("Final and initial structure has "
                                     "different number of each species")

            self.insert_structure(init_struct=init, final_struct=final)
            num_ins += 1
            cb(num_ins, len(traj_in))

    def insert_structure(self,
                         init_struct: Union[Atoms, str],
                         final_struct: Optional[Union[Atoms, str]] = None,
                         name: Optional[str] = None,
                         cf: Optional[Dict[str, float]] = None) -> None:
        """Insert a structure to the database.

        :param init_struct: Unrelaxed initial structure. If a string is passed,
            it should be the file name with .xyz, .cif or .traj extension.
        :param final_struct: (Optional) final structure that contains energy.
            It can be either ASE Atoms object or file anme ending with .traj.
        :param name: (Optional) name of the DB entry if a custom name is to be
            used. If `None`, default naming convention will be used.
        :param cf: (Optional) full correlation function of the initial
            structure (correlation functions with zero values should also be
            included). If cf is given, the preprocessing of the init_structure
            is bypassed and the given cf is inserted in DB.
        """
        if name is not None:
            with connect(self.settings.db_name) as db:
                cur = db.connection.cursor()
                cur.execute("SELECT id FROM text_key_values WHERE key=? and value=?",
                            ("name", name))
                num = len(cur.fetchall())
            if num > 0:
                raise ValueError(f"Name: {name} already exists in DB!")

        if cf is None:
            if isinstance(init_struct, Atoms):
                init_struct = wrap_and_sort_by_position(init_struct)
            else:
                init_struct = wrap_and_sort_by_position(read(init_struct))
            cf = self.corrfunc.get_cf(init_struct)

        self.settings.set_active_template(atoms=init_struct)

        formula_unit = self._get_formula_unit(init_struct)
        if self._exists_in_db(init_struct, formula_unit):
            logger.warning(
                ("Supplied structure already exists in DB. The structure will not be inserted."))
            return

        kvp = self._get_kvp(formula_unit)

        if name is not None:
            kvp['name'] = name
        kvp['converged'] = False
        kvp['started'] = False
        kvp['queued'] = False
        kvp['struct_type'] = 'initial'
        tab_name = self.corr_func_table_name
        uid_init = db_util.new_row_with_single_table(self.db, init_struct, tab_name, cf, **kvp)

        if final_struct is not None:
            if not isinstance(final_struct, Atoms):
                final_struct = read(final_struct)
            kvp_final = {'struct_type': 'final', 'name': kvp['name']}
            uid = self.db.write(final_struct, kvp_final)
            self.db.update(uid_init, converged=True, started='', queued='', final_struct_id=uid)

    def _exists_in_db(self, atoms: Atoms, formula_unit: Optional[str] = None) -> bool:
        """
        Check to see if the passed atoms already exists in DB.

        To reduce the number of assessments for symmetry equivalence,
        check is only performed with the entries with the same concentration
        value.

        Return *True* if there is a symmetry-equivalent structure in DB,
        return *False* otherwise.

        :param atoms: Structure to be compared against the rest of structures
            in DB.
        :formula_unit: Reduced formula unit of the passed Atoms object
        """
        cond = [('name', '!=', 'template'), ('name', '!=', 'primitive_cell')]
        if formula_unit is not None:
            cond.append(("formula_unit", "=", formula_unit))

        to_prim = True
        try:
            __import__('spglib')
        except ImportError:
            logger.warning("Setting 'to_primitive=False' because spglib is missing!")
            to_prim = False

        symmcheck = SymmetryEquivalenceCheck(angle_tol=1.0,
                                             ltol=0.05,
                                             stol=0.05,
                                             scale_volume=True,
                                             to_primitive=to_prim)

        atoms_in_db = []
        for row in self.db.select(cond):
            atoms_in_db.append(row.toatoms())

        return symmcheck.compare(atoms.copy(), atoms_in_db)

    def _get_kvp(self, formula_unit: str = None) -> Dict:
        """
        Create a dictionary of key-value pairs and return it.

        :param atoms: ASE Atoms object for which the key-value pair
            descriptions will be generated
        :param formula_unit: reduced formula unit of the passed Atoms object
        """
        if formula_unit is None:
            raise ValueError("Formula unit not specified!")
        kvp = {}
        kvp['gen'] = self.gen
        kvp['converged'] = False
        kvp['started'] = False
        kvp['queued'] = False

        suffixes = []
        logger.debug('Connecting to %s', self.settings.db_name)
        with connect(self.settings.db_name) as db:
            cur = db.connection.cursor()
            logger.debug("Selecting from db: formula_unit=%s", formula_unit)
            cur.execute("SELECT id FROM text_key_values WHERE key=? AND value=?",
                        ("formula_unit", formula_unit))
            ids = [i[0] for i in cur.fetchall()]
            for row_id in ids:
                logger.debug('Selecting from db: name=%s', row_id)
                cur.execute("SELECT value FROM text_key_values WHERE key=? AND id=?",
                            ("name", row_id))
                name = cur.fetchone()[0]
                suffix = 0
                if "_" in name:
                    suffix = int(name.rpartition("_")[-1])
                suffixes.append(suffix)
        suffixes.sort()

        suffix = len(suffixes)
        for i, s in enumerate(suffixes):
            if i != s and i not in suffixes:
                suffix = i
                break

        suffix = min(suffix, len(suffixes))
        kvp['name'] = formula_unit + f"_{suffix}"
        kvp['formula_unit'] = formula_unit
        kvp['struct_type'] = 'initial'
        size = self.settings.size
        if size is not None:
            # We do not store the size if it is None
            size = nested_list2str(self.settings.size)
            kvp['size'] = size
        return kvp

    def _get_formula_unit(self, atoms: Atoms) -> str:
        """Generates a reduced formula unit for the structure."""
        atom_count = []
        all_nums = []
        for group in self.settings.index_by_basis:
            new_count = {}
            for indx in group:
                symbol = atoms[indx].symbol
                if symbol not in new_count:
                    new_count[symbol] = 1
                else:
                    new_count[symbol] += 1
            atom_count.append(new_count)
            all_nums += [v for k, v in new_count.items()]
        # pylint: disable=unnecessary-lambda
        gcdp = reduce(lambda x, y: gcd(x, y), all_nums)
        fu = ""
        for i, count in enumerate(atom_count):
            keys = list(count.keys())
            keys.sort()
            for k in keys:
                fu += f"{k}{int(count[k] / gcdp)}"
            if i < len(atom_count) - 1:
                fu += "_"
        return fu

    def _random_struct_at_conc(self, num_atoms_to_insert: np.ndarray) -> Atoms:
        """Generate a random structure."""
        rnd_indices = []
        for indices in self.settings.index_by_basis:
            rnd_indices.append(deepcopy(indices))
            shuffle(rnd_indices[-1])

        # Insert the number of atoms
        basis_elem = self.settings.concentration.basis_elements
        assert len(rnd_indices) == len(basis_elem)
        atoms = self.settings.atoms.copy()
        current_conc = 0
        num_atoms_inserted = 0

        for basis, indices in enumerate(rnd_indices):
            current_indx = 0
            for symb in basis_elem[basis]:
                for _ in range(num_atoms_to_insert[current_conc]):
                    atoms[indices[current_indx]].symbol = symb
                    current_indx += 1
                    num_atoms_inserted += 1
                current_conc += 1
        assert num_atoms_inserted == len(atoms)
        return atoms

    def _determine_gen_number(self) -> int:
        """Determine generation number based on the values in DB."""
        with connect(self.settings.db_name) as db:
            cur = db.connection.cursor()
            cur.execute("SELECT value FROM number_key_values WHERE key='gen'")
            gens = [int(i[0]) for i in cur.fetchall()]
            if len(gens) == 0:
                gen = 0
            else:
                gen = max(gens)
                cur.execute("SELECT id FROM number_key_values WHERE key=? AND value=?",
                            ("gen", gen))
                num_in_gen = len(cur.fetchall())
                if num_in_gen >= self.struct_per_gen:
                    gen += 1
        return gen

    def _generate_sigma_mu(self, num_samples_var: int) -> None:
        """
        Generate sigma and mu of eq.3 in PRB 80, 165122 (2009) and save them
        in `probe_structure-sigma_mu.npz` file.

        :param num_samples_var: number of samples to be used in determining
                                signam and mu.
        """
        logger.info(('===========================================================\n'
                     'Determining sigma and mu value for assessing mean variance.\n'
                     'May take a long time depending on the number of samples \n'
                     'specified in the *num_samples_var* argument, which is %d.\n'
                     '==========================================================='),
                    num_samples_var)
        count = 0
        cfm = np.zeros((num_samples_var, len(self.settings.all_cf_names)), dtype=float)
        while count < num_samples_var:
            atoms = self._get_struct_at_conc(conc_type='random')
            cfm[count] = self.corrfunc.get_cf(atoms)
            count += 1
            logger.info("Sampling %d ouf of %d", count, num_samples_var)

        sigma = np.cov(cfm.T)
        mu = np.mean(cfm, axis=0)
        fname = 'probe_structure-sigma_mu.npz'  # Should probably be a variable
        np.savez(fname, sigma=sigma, mu=mu)
        logger.debug('Saved sigma and mu in %s', fname)
