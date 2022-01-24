from typing import Dict
from ase import Atoms
from clease.settings import ClusterExpansionSettings
from clease.tools import wrap_and_sort_by_position
from .clease import Clease


def attach_calculator(settings: ClusterExpansionSettings,
                      atoms: Atoms,
                      eci: Dict[str, float] = None) -> Atoms:
    """Utility function for an efficient initialization of large cells.

    :param settings: ClusterExpansionSettings object (e.g., CEBulk, CECyrstal)
    :param eci: Dictionary containing cluster names and their ECI values
    :param atoms: ASE Atoms object.
    """
    if eci is None:
        eci = {}

    template = settings.template_atoms.get_template_matching_atoms(atoms=atoms)
    settings.set_active_template(atoms=template)

    wrapped = wrap_and_sort_by_position(atoms.copy())
    atoms_with_calc = settings.atoms.copy()

    calc = Clease(settings, eci=eci)
    atoms_with_calc.symbols = wrapped.symbols
    atoms_with_calc.calc = calc

    return atoms_with_calc


def get_ce_energy(settings: ClusterExpansionSettings, atoms: Atoms, eci: Dict[str, float]) -> float:
    """Get energy of the ASE Atoms object based on given ECI values.

    :param settings: ClusterExpansionSettings object (e.g., CEBulk, CECyrstal)
    :param atoms: ASE Atoms object representing the considered atomic
        arrangement
    :param eci: ECI values to be used to calculate the energy
    """
    # temp atoms to avoid making unexpected changes to passed atoms
    temp_atoms = atoms.copy()
    calc = Clease(settings, eci=eci)
    temp_atoms.calc = calc
    energy = temp_atoms.get_potential_energy()
    return energy
