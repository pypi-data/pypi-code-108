from __future__ import annotations

import itertools as it
from collections import defaultdict
from typing import DefaultDict, Dict

from .data import Compound, Reaction

__all__ = [
    "check_compound_existence",
    "check_mass_balance",
    "check_charge_balance",
    "reaction_is_bad",
]


def check_compound_existence(rxn: Reaction, cpds: Dict[str, Compound]) -> bool:
    """Check if all compounds of a reaction exist."""
    for cpd in it.chain(rxn.substrates, rxn.products):
        if cpd not in cpds:
            return False
    return True


def check_mass_balance(rxn: Reaction, cpds: Dict[str, Compound]) -> bool:
    """Check if the reaction is mass-balanced."""
    lhs, rhs = rxn.substrates, rxn.products

    lhs_atoms: DefaultDict[str, float] = defaultdict(lambda: 0.0)
    rhs_atoms: DefaultDict[str, float] = defaultdict(lambda: 0.0)

    for cpd, stoich in lhs.items():
        formula = cpds[cpd].formula
        # Check if compound has a formula in the first place
        if not bool(formula):
            return False
        for atom, count in formula.items():
            lhs_atoms[atom] -= count * stoich

    for cpd, stoich in rhs.items():
        # Check if compound has a formula in the first place
        formula = cpds[cpd].formula
        if not bool(formula):
            return False
        for atom, count in formula.items():
            rhs_atoms[atom] += count * stoich

    for k in set((*lhs_atoms, *rhs_atoms)):
        diff = lhs_atoms[k] - rhs_atoms[k]
        if diff != 0:
            return False
    return True


def check_charge_balance(rxn: Reaction, cpds: Dict[str, Compound]) -> bool:
    """Check if the reaction is charge-balanced."""
    lhs_charge, rhs_charge = 0.0, 0.0
    for cpd, stoich in rxn.substrates.items():
        try:
            lhs_charge -= stoich * cpds[cpd].charge
        except TypeError:
            return False
    for cpd, stoich in rxn.products.items():
        try:
            rhs_charge += stoich * cpds[cpd].charge
        except TypeError:
            return False
    if lhs_charge - rhs_charge == 0:
        return True
    return False


def reaction_is_bad(rxn: Reaction, cpds: Dict[str, Compound]) -> bool:
    if not check_compound_existence(rxn, cpds):
        return True
    if not check_mass_balance(rxn, cpds):
        return True
    if not check_charge_balance(rxn, cpds):
        return True
    return False
