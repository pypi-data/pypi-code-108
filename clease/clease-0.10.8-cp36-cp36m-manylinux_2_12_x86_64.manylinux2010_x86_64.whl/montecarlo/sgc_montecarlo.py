from typing import Sequence, Dict
import numpy as np
from ase import Atoms
from ase.units import kB
from .observers import SGCObserver
from .montecarlo import Montecarlo
from .trial_move_generator import TrialMoveGenerator, RandomFlip


class InvalidChemicalPotentialError(Exception):
    pass


# pylint: disable=too-many-instance-attributes
class SGCMonteCarlo(Montecarlo):
    """
    Class for running Monte Carlo in the Semi-Grand Canonical Ensebmle
    (i.e., fixed number of atoms, but varying composition)

    See the docstring of :class:`clease.montecarlo.Montecarlo`

    :param atoms: Atoms object (with CLEASE calculator attached!)
    :param temp: Temperature in kelvin
    :param symbols: Possible symbols to be used in swaps
    :param generator: Generator that produces trial moves
    """

    def __init__(self,
                 atoms: Atoms,
                 temp: float,
                 symbols: Sequence[str] = (),
                 generator: TrialMoveGenerator = None):
        if generator is None:
            if len(symbols) <= 1:
                raise ValueError("At least 2 symbols have to be specified")
            generator = RandomFlip(symbols, atoms)
        super().__init__(atoms, temp, generator=generator)
        self.symbols = symbols

        self.averager = SGCObserver(self.atoms.calc)

        self.chem_pots = []
        self.chem_pot_names = []
        self.has_attached_avg = False
        self.name = "SGCMonteCarlo"
        self._chemical_potential = None
        self.chem_pot_in_eci = False
        self.current_singlets = None

        has_attached_obs = False
        for obs in self.observers:
            if obs.name == "SGCObserver":
                has_attached_obs = True
                self.averager = obs
                break
        if not has_attached_obs:
            self.attach(self.averager)

    def _check_symbols(self):
        """
        Override because there are no restriction on the symbols here
        """

    def reset(self):
        """
        Reset the simulation object
        """
        super().reset()
        self.averager.reset()

    @property
    def chemical_potential(self):
        return self._chemical_potential

    @chemical_potential.setter
    def chemical_potential(self, chem_pot: Dict[str, float]):
        eci = self.atoms.calc.eci
        if any(key not in eci for key in chem_pot):
            msg = "A chemical potential not being trackted is added. Make "
            msg += "sure that all the following keys are in the ECIs before "
            msg += "they are passed to the calculator: "
            msg += f"{list(chem_pot.keys())}\n"
            msg += "(Add them with a zero ECI value if they are not supposed "
            msg += "to be included.)"
            raise InvalidChemicalPotentialError(msg)

        self._chemical_potential = chem_pot
        if self.chem_pot_in_eci:
            self._reset_eci_to_original(self.atoms.calc.eci)
        self._include_chemical_potential_in_eci(chem_pot, self.atoms.calc.eci)

    def _include_chemical_potential_in_eci(self, chem_pot: Dict[str, float], eci: Dict[str, float]):
        """
        Including the chemical potentials in the ECIs

        Parameters:


        chem_pot: dict
            Chemical potentials
        eci: dict
            Original ECIs
        """
        self.chem_pots = []
        self.chem_pot_names = []
        keys = list(chem_pot.keys())
        keys.sort()
        for key in keys:
            self.chem_pots.append(chem_pot[key])
            self.chem_pot_names.append(key)
            current_eci = eci.get(key, 0.0)
            eci[key] = current_eci - chem_pot[key]
        calc = self.atoms.calc
        calc.update_eci(eci)
        self.chem_pot_in_eci = True
        self.current_energy = calc.calculate(None, None, None)
        return eci

    def _reset_eci_to_original(self, eci_with_chem_pot: Dict[str, float]):
        """
        Resets the ECIs to their original value

        :parma dict eci_with_chem_pot: ECIs with chemical potential included
        """
        for name, val in zip(self.chem_pot_names, self.chem_pots):
            eci_with_chem_pot[name] += val
        calc = self.atoms.calc
        calc.update_eci(eci_with_chem_pot)
        self.chem_pot_in_eci = False
        self.current_energy = calc.calculate(None, None, None)
        return eci_with_chem_pot

    def reset_eci(self):
        """Return the ECIs."""
        if self.chem_pot_in_eci:
            self._reset_eci_to_original(self.atoms.calc.eci)

    # pylint: disable=arguments-differ
    def run(self, steps: int = 10, chem_pot: Dict[str, float] = None):
        """
        Run Monte Carlo simulation.
        See :py:meth:`cemc.mcmc.Montecarlo.runMC`

        Parameters:

        chem_pot: dict
            Chemical potentials. The keys should correspond to one of the
            singlet terms. A typical form of this is {"c1_0":-1.0,c1_1_1.0}
        """

        if chem_pot is None and self.chemical_potential is None:
            ex_chem_pot = {"c1_1": -0.1, "c1_2": 0.05}
            raise ValueError(f"No chemicalpotentials given. Has to be "
                             f"dictionary of the form {ex_chem_pot}")

        if chem_pot is not None:
            self.chemical_potential = chem_pot
        self.reset()

        Montecarlo.run(self, steps=steps)

    def singlet2composition(self, avg_singlets: Dict[str, float]):
        """Convert singlets to composition."""
        bf = self.atoms.calc.settings.basis_functions
        matrix = np.zeros((len(self.symbols), len(self.symbols)))

        index = {s: i for i, s in enumerate(self.symbols)}
        for i, b in enumerate(bf):
            for s, col in index.items():
                matrix[i, col] = b[s]

        matrix[-1, :] = 1.0
        rhs = np.zeros(len(self.symbols))
        rhs[:-1] = avg_singlets
        rhs[-1] = 1.0
        x = np.linalg.solve(matrix, rhs)

        res = {}
        for s, i in index.items():
            name = s + "_conc"
            res[name] = x[i]
        return res

    # pylint: disable=arguments-differ
    def get_thermodynamic_quantities(self, reset_eci=True):
        """Compute thermodynamic quantities.

        Parameters:

        reset_eci: bool
            If True, the chemical potential will be removed from the ECIs
        """
        N = self.averager.counter
        quantities = {}
        singlets = self.averager.singlets / N
        singlets_sq = self.averager.quantities["singlets_sq"] / N

        quantities["sgc_energy"] = self.averager.energy.mean
        quantities["sgc_heat_capacity"] = self.averager.energy_sq.mean - \
            self.averager.energy.mean**2

        quantities["sgc_heat_capacity"] /= (kB * self.T**2)

        quantities["energy"] = self.averager.energy.mean
        natoms = len(self.atoms)
        for i, chem_pot in enumerate(self.chem_pots):
            quantities["energy"] += chem_pot * singlets[i] * natoms

        quantities["temperature"] = self.T
        quantities["n_mc_steps"] = self.averager.counter

        # Add singlets and chemical potential to the dictionary
        # pylint: disable=consider-using-enumerate
        for i in range(len(singlets)):
            name = f"singlet_{self.chem_pot_names[i]}"
            quantities[name] = singlets[i]

            name = f"var_singlet_{self.chem_pot_names[i]}"
            quantities[name] = singlets_sq[i] - singlets[i]**2

            name = f"mu_{self.chem_pot_names[i]}"
            quantities[name] = self.chem_pots[i]

        quantities.update(self.meta_info)

        try:
            avg_conc = self.singlet2composition(singlets)
            quantities.update(avg_conc)
        # pylint: disable=broad-except
        except Exception as exc:
            print("Could not find average singlets!")
            print(exc)

        if reset_eci:
            self._reset_eci_to_original(self.atoms.calc.eci)
        return quantities
