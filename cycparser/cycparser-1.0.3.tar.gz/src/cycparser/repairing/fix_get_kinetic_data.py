from __future__ import annotations

from typing import Dict

from ..data import Enzyme, KineticData, Reaction


def get_kinetic_data(
    reactions: Dict[str, Reaction],
    enzymes: Dict[str, Enzyme],
) -> Dict[str, Dict[str, KineticData]]:
    res: Dict[str, Dict[str, KineticData]] = {}
    for name, reaction in reactions.items():
        for enzyme in reaction.enzrxns:
            res.setdefault(name, {}).setdefault(enzyme, enzymes[enzyme].kinetic_data)
    return res
