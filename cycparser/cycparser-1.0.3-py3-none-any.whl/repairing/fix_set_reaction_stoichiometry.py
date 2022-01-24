from __future__ import annotations

from typing import Dict

from ..data import Reaction


def fix_set_reaction_stoichiometry(parse_reactions: Dict[str, Reaction]) -> Dict[str, Reaction]:
    """Set the stoichiometry from the information given by the substrates and products."""
    new_reactions = {}
    for rxn_id, reaction in parse_reactions.items():
        substrates = reaction.substrates
        products = reaction.products

        # Check for duplicates
        for compound in set(substrates).intersection(set(products)):
            diff = products[compound] - abs(substrates[compound])
            if diff == 0:
                del substrates[compound]
                del products[compound]
            elif diff < 0:
                substrates[compound] = diff
                del products[compound]
            else:
                del substrates[compound]
                products[compound] = diff

        # Create stoichiometry
        stoichiometries = {**substrates, **products}
        if len(stoichiometries) > 1:
            reaction.stoichiometries = stoichiometries
            new_reactions[rxn_id] = reaction
    return new_reactions
