from __future__ import annotations

from typing import Dict

from ..data import Compound, Reaction
from ..utils import reaction_is_bad


def fix_filter_garbage_reactions(
    rxns: Dict[str, Reaction],
    cpds: Dict[str, Compound],
) -> Dict[str, Reaction]:
    new_reactions = {}
    for rxn_id, reaction in rxns.items():
        if reaction_is_bad(reaction, cpds):
            continue
        new_reactions[rxn_id] = reaction
    return new_reactions
