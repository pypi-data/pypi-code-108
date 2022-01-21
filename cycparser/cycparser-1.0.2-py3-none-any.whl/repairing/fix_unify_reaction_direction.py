from __future__ import annotations

import logging
from typing import Dict

from ..data import Reaction

logger = logging.getLogger(__name__)


def _reverse_stoichiometry(rxn: Reaction) -> None:
    """Reverse the stoichiometry of a reaction.

    This also reverses the compartments and the gibbs0.
    """
    substrates = rxn.substrates.copy()
    products = rxn.products.copy()
    rxn.substrates = {k: -v for k, v in products.items()}
    rxn.products = {k: -v for k, v in substrates.items()}
    if rxn.gibbs0 is not None:
        rxn.gibbs0 = -rxn.gibbs0
    rxn.substrate_compartments, rxn.product_compartments = (
        rxn.product_compartments,
        rxn.substrate_compartments,
    )


def fix_unify_reaction_direction(parse_reactions: Dict[str, Reaction]) -> Dict[str, Reaction]:
    """Set every reaction to be LEFT-TO-RIGHT and add bounds accordingly."""
    for reaction in parse_reactions.values():
        if reaction.reversible:
            reaction.bounds = (-1000, 1000)
        else:
            direction = reaction.direction
            if direction in (
                "LEFT-TO-RIGHT",
                "PHYSIOL-LEFT-TO-RIGHT",
                "IRREVERSIBLE-LEFT-TO-RIGHT",
            ):
                reaction.bounds = (0, 1000)
            elif direction in (
                "RIGHT-TO-LEFT",
                "PHYSIOL-RIGHT-TO-LEFT",
                "IRREVERSIBLE-RIGHT-TO-LEFT",
            ):
                _reverse_stoichiometry(reaction)
                reaction.bounds = (0, 1000)
            else:
                logger.info(
                    f"Weird reaction direction '{direction}' for reaction {reaction.id}, setting to LEFT-TO-RIGHT"
                )
                reaction.bounds = (0, 1000)
    return parse_reactions
