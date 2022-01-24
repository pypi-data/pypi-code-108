from typing import Dict, Optional, Iterable, Set, List, Union, Sequence
from ase import Atoms
from ase.calculators.calculator import Calculator
from clease.datastructures import SystemChange
from clease.settings import ClusterExpansionSettings
from .clease import Clease


class CleaseVolDep(Clease):
    """
    Calculator that can be used together with volume dependent ECIs

    :param settings: ClusterExpansionSettings object used to construct the
        cluster expansion
    :param eci: Dictionary with ECI. The keys in the dictionary should have the
        following form: c<size>_<diameter>_<id>_<decoration_number>_V<power>.
        Example: if the contribution to the total energy from the
        nearest neighbour pair cluster has the mathematical form

        (A + B*V + C*V^2)*CF,

        where CF is the nearest neighbour pair correlation function, the
        following coefficients should be in the ECI dict (the id is 0 and
        decoration number 00 in this example. They could be different for other
        correlation functions)

        {
            'c2_d0000_0_00_V0': A,
            'c2_d0000_0_00_V1': B,
            'c2_d0000_0_00_V2': C
        }

        The total energy is given by a sum of terms of the form depicted above.
        Example: If the total energy depends on the one-body, nearest neighbour
        pair cluster and shorted three body cluster with correlation functions
        CF1, CF2 and CF3, respectively. The expression for the total energy is

        E = (A1 + B1*V + C1*V^2)*CF1 + (A2 + B2*V + C2*V^2)*CF2 +
            (A3 + B3*V + C3*V^2)*CF3

        the ECI dictionary required to represent this expression is

        {
            'c1_0_V0': A1,
            'c1_0_V1': B1,
            'c1_0_V3': C1,
            'c2_d0000_0_00_V0': A2,
            'c2_d0000_0_00_V1': B2,
            'c2_d0000_0_00_V2': C2,
            'c3_d0000_0_000_V0': A3,
            'c3_d0000_0_000_V1': B3,
            'c3_d0000_0_000_V2': C3,
        }

        again the id has been set to 0 and the decoration numbers are only 00
        (and 000), which will vary for different types of correlation functions.
    :param vol_coeff: Expansion coefficients used to cluster expand the volume.
        The volume coefficients should not have the V<power> tag at the end.
        Example: If the volume can be described by the following mathematical
        form

        V = A + B*CF1 + C*CF2,

        where CF1 is the correlation function of one-body clusters and CF2 is
        the correlation function of the nearest neighbour pair interacation,
        the passed dictionary should be

        {
            'c0': A,
            'c1_0': B,
            'c2_d0000_0_00': C
        }
    :param init_cf: Correlation functions of the initial atoms object. They can
        for instance be obtained via `clease.CorrFunction`. If not passed,
        they are calculated from scratch when an atoms object is attached.
    """

    def __init__(self,
                 settings: ClusterExpansionSettings,
                 eci: Dict[str, float],
                 vol_coeff: Dict[str, float],
                 init_cf: Optional[Dict[str, float]] = None):

        if not eci_format_ok(eci.keys()):
            raise ValueError(f"Invalid format of ECI names. Got\n{eci.keys()}")

        if not vol_coeff_format_ok(vol_coeff.keys()):
            raise ValueError("Invalid format of volume coefficient names. "
                             f"Got\n{vol_coeff.keys()}")

        cf_to_track = unique_eci_names_no_vol(eci.keys())
        cf_to_track = cf_to_track.union(set(vol_coeff.keys()))

        # Create a set of empty ECI and pass to the parent class.
        # This makes sure that all nessecary correlation functions
        # are tracked.
        eci_track = {k: 0.0 for k in cf_to_track}

        # Transfer the volume independent part to the parent calculator
        for k, v in eci.items():
            if k.endswith('V0'):
                key = k.rpartition('_V0')[0]
                eci_track[key] = v

        Clease.__init__(self, settings, eci_track, init_cf=init_cf)
        self.eci_with_vol = eci
        self.vol_coeff = vol_coeff
        self.max_power = max(int(k[-1]) for k in self.eci_with_vol.keys())

    def get_volume(self, cf: Optional[Dict[str, float]] = None) -> float:
        """
        Returns the volume per atom

        :param cf: Correlation functions. If not given, the correlation
            functions are updated to match the current state of the attached
            atoms object
        """
        if cf is None:
            self.update_cf(None)
            cf = self.get_cf()
        vol = sum(self.vol_coeff[k] * cf[k] for k in self.vol_coeff)
        self.results['volume_per_atom'] = vol
        self.results['volume'] = vol * len(self.atoms)
        return vol

    def get_pressure(self, cf: Optional[Dict[str, float]] = None) -> float:
        """
        Return the pressure

        :param cf: Correlation functions. If not given, the correlation
            functions are updated to match the current state of the attached
            atoms object
        """
        if cf is None:
            self.update_cf(None)
            cf = self.get_cf()

        vol = self.get_volume(cf)
        P = sum(p * self.eci_with_vol.get(k + f"_V{p}", 0.0) * cf[k] * vol**(p - 1)
                for k in cf.keys()
                for p in range(1, self.max_power + 1))
        self.results['pressure'] = P
        return P

    def get_bulk_modulus(self, cf: Optional[Dict[str, float]] = None) -> float:
        """
        Return the bulk modulus of the current atoms object

        :param cf: Correlation functions. If not given, the correlation
            functions are updated to match the current state of the attached
            atoms object
        """
        if cf is None:
            self.update_cf(None)
            cf = self.get_cf()

        vol = self.get_volume(cf)
        B = vol * self._d2EdV2(cf, vol)
        self.results['bulk_mod'] = B
        return B

    def _d2EdV2(self, cf: Dict[str, float], vol: float) -> float:
        """
        Return the double derivative of the energy with respect
        to the volume

        :param cf: Correlation functions
        :param vol: Volume
        """
        return sum(p * (p - 1) * self.eci_with_vol.get(k + f"_V{p}", 0.0) * cf[k] * vol**(p - 2)
                   for k in cf.keys()
                   for p in range(2, self.max_power + 1))

    def _d3EdV3(self, cf: Dict[str, float], vol: float) -> float:
        """
        Return the third derivative of the energy with respect to
        the volume

        :param cf: Correlation functions
        :param vol: Volume
        """
        return sum(p * (p - 1) * (p - 2) * self.eci_with_vol.get(k + f"_V{p}", 0.0) * cf[k] *
                   vol**(p - 3) for k in cf.keys() for p in range(3, self.max_power + 1))

    def get_dBdP(self, cf: Dict[str, float] = None) -> float:
        """
        Return the pressure derivative of the bulk modulus of the
        current structure.

        :param cf: Correlation functions. If not given, the correlation
            functions are updated to match the current state of the attached
            atoms object
        """
        if cf is None:
            self.update_cf(None)
            cf = self.get_cf()
        vol = self.get_volume(cf)
        return -1.0 - vol * self._d3EdV3(cf, vol) / self._d2EdV2(cf, vol)

    def get_energy_given_change(self, system_changes: Sequence[SystemChange], keep_changes=False):
        """
        Update correlation functions given the change
        """
        with self.with_system_changes(system_changes) as keeper:
            keeper.keep_changes = keep_changes
            cf = self.get_cf()
            vol = self.get_volume(cf)
            energy = sum(
                self.eci_with_vol.get(k + f"_V{p}", 0.0) * cf[k] * vol**p
                for k in cf.keys()
                for p in range(self.max_power + 1))
            self.energy = energy * len(self.atoms)
            self.results['energy'] = self.energy
            return self.energy

    def calculate(self, atoms: Atoms, properties: List[str],
                  system_changes: Union[Sequence[SystemChange], None]) -> float:
        """Calculate the energy of the passed Atoms object.

        If accept=True, the most recently used atoms object is used as a
        reference structure to calculate the energy of the passed atoms.
        Returns energy.

        Parameters:

        :param atoms: ASE Atoms object

        :param system_changes:
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """
        Calculator.calculate(self, atoms)
        self.update_cf()
        return self.get_energy_given_change([], keep_changes=True)

    def _on_eci_changed(self):
        """
        Callback triggered by the parent class when the ECIs are changed.
        """
        for k, v in self.eci.items():
            vol_dep_key = k + '_V0'
            self.eci_with_vol[vol_dep_key] = v


def unique_eci_names_no_vol(eci_names: Iterable[str]) -> Set[str]:
    """
    Return a set with the unique ECI names without any volume tag
    """
    eci_no_vol = set(k.rpartition('_V')[0] for k in eci_names)
    return eci_no_vol


def eci_format_ok(eci_names: Iterable[str]) -> bool:
    """
    Check that all ECIs are formatted correctly.
    """
    for name in eci_names:
        valid = name.startswith('c') and '_V' in name
        if not valid:
            return False
    return True


def vol_coeff_format_ok(vol_coeff_names: Iterable[str]) -> bool:
    """
    Check that the volume coefficients are valid
    """
    for name in vol_coeff_names:
        valid = name.startswith('c') and '_V' not in name
        if not valid:
            return False
    return True
