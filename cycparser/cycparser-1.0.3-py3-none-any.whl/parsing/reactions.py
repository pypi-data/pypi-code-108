from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Dict, Iterable

from ..data import Reaction
from .shared import (
    MALFORMED_LINE_STARTS,
    _add_database_link,
    _add_type,
    _rename,
    _set_gibbs0,
    _set_name,
)

__all__ = ["parse_reactions"]

logger = logging.getLogger(__name__)
Action = Callable[[Any, Any, Any], None]
SubAction = Dict[str, Callable[[Any, Any, Any, Any], None]]


def _set_ec_number(reactions: Dict[str, Reaction], id_: str, ec_number: str) -> None:
    reactions[id_].ec = ec_number


def _add_reaction_pathway(reactions: Dict[str, Reaction], id_: str, pathway: str) -> None:
    reactions[id_].pathways.add(pathway)


def _add_enzrxn(reactions: Dict[str, Reaction], id_: str, enzrxn: str) -> None:
    reactions[id_].enzrxns.add(enzrxn)


def _set_reaction_direction(reactions: Dict[str, Reaction], id_: str, direction: str) -> None:
    reactions[id_].direction = direction
    if direction == "REVERSIBLE":
        reactions[id_].reversible = True
    else:
        reactions[id_].reversible = False


def _add_reaction_location(reactions: Dict[str, Reaction], id_: str, location: str) -> None:
    location = location.replace("CCI-", "CCO-")
    if location.startswith("CCO-"):
        reactions[id_].locations.append(location)


def _set_substrate(
    reactions: Dict[str, Reaction],
    id_: str,
    substrate: str,
    type_map: Dict[str, str],
) -> None:
    substrate = _rename(type_map.get(substrate, substrate)) + "_c"
    reactions[id_].substrates[substrate] = -1
    reactions[id_].substrate_compartments[substrate] = "CCO-IN"


def _set_product(
    reactions: Dict[str, Reaction],
    id_: str,
    product: str,
    type_map: Dict[str, str],
) -> None:
    product = _rename(type_map.get(product, product)) + "_c"
    reactions[id_].products[product] = 1
    reactions[id_].product_compartments[product] = "CCO-IN"


def _set_substrate_coefficient(
    reactions: Dict[str, Reaction],
    id_: str,
    coefficient: str,
    substrate: str,
    type_map: Dict[str, str],
) -> None:
    try:
        reactions[id_].substrates[_rename(type_map.get(substrate, substrate)) + "_c"] = -float(coefficient)
    except ValueError:  # conversion failed
        pass


def _set_product_coefficient(
    reactions: Dict[str, Reaction],
    id_: str,
    coefficient: str,
    product: str,
    type_map: Dict[str, str],
) -> None:
    try:
        reactions[id_].products[_rename(type_map.get(product, product)) + "_c"] = float(coefficient)
    except ValueError:  # conversion failed
        pass


def _set_substrate_compartment(
    reactions: Dict[str, Reaction],
    id_: str,
    compartment: str,
    substrate: str,
    type_map: Dict[str, str],
) -> None:
    substrate = _rename(type_map.get(substrate, substrate)) + "_c"
    if compartment == "CCO-OUT":
        reactions[id_].substrate_compartments[substrate] = compartment
    elif compartment == "CCO-MIDDLE":
        reactions[id_].substrate_compartments[substrate] = "CCO-OUT"
    else:
        # reactions[id_].product_compartments[substrate] = "CCO-OUT"
        logger.info(f"Unknown compartment {compartment}")


def _set_product_compartment(
    reactions: Dict[str, Reaction],
    id_: str,
    compartment: str,
    product: str,
    type_map: Dict[str, str],
) -> None:
    product = _rename(type_map.get(product, product)) + "_c"
    if compartment == "CCO-OUT":
        reactions[id_].product_compartments[product] = compartment
    elif compartment == "CCO-MIDDLE":
        reactions[id_].product_compartments[product] = "CCO-OUT"
    else:
        # reactions[id_].product_compartments[product] = "CCO-OUT"
        logger.info(f"Unknown compartment {compartment}")


def parse_reactions(
    file: Iterable[str],
    type_map: Dict[str, str],
    actions: Dict[str, Action] | None = None,
    sub_actions: Dict[str, SubAction] | None = None,
    db_to_resource: dict[str, str] | None = None,
) -> Dict[str, Reaction]:
    if db_to_resource is None:
        db_to_resource = {
            "BIGG": "bigg.reaction",
            "METANETX-RXN": "metanetx.reaction",
            "RHEA": "rhea",
            "PIR": "pirsf",
            "UNIPROT": "uniprot",
            "SEED": "seed.reaction",
        }

    if actions is None:
        actions = {
            "TYPES": partial(_add_type, type_map=type_map),
            "COMMON-NAME": _set_name,
            "DBLINKS": partial(_add_database_link, db_to_resource=db_to_resource),
            "EC-NUMBER": _set_ec_number,
            "ENZYMATIC-REACTION": _add_enzrxn,
            "GIBBS-0": _set_gibbs0,
            "IN-PATHWAY": _add_reaction_pathway,
            "LEFT": partial(_set_substrate, type_map=type_map),
            "REACTION-DIRECTION": _set_reaction_direction,
            "RIGHT": partial(_set_product, type_map=type_map),
            "RXN-LOCATIONS": _add_reaction_location,
        }

    if sub_actions is None:
        sub_actions = {
            "^COMPARTMENT": {
                "LEFT": partial(_set_substrate_compartment, type_map=type_map),
                "RIGHT": lambda a, b, c, d: _set_product_compartment(a, b, c, d, type_map=type_map),
            },
            "^COEFFICIENT": {
                "LEFT": lambda a, b, c, d: _set_substrate_coefficient(a, b, c, d, type_map=type_map),
                "RIGHT": lambda a, b, c, d: _set_product_coefficient(a, b, c, d, type_map=type_map),
            },
        }

    id_ = ""
    reactions = {}
    last_identifier = ""
    last_content = ""
    for line in file:
        if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
            continue
        try:
            identifier, content = line.rstrip().split(" - ", maxsplit=1)
        except ValueError:
            logger.info(f"Malformed line in reactions.dat: {line}")
            continue

        if identifier == "UNIQUE-ID":
            id_ = content
            reactions[id_] = Reaction(
                id=id_,
                base_id=id_,
                database_links={
                    "biocyc": set([id_]),
                    "metacyc.reaction": set([id_]),
                },
            )
        elif identifier.startswith("^"):
            if (subaction := sub_actions.get(identifier, {}).get(last_identifier, None)) is not None:
                subaction(reactions, id_, content, last_content)
        else:
            if (action := actions.get(identifier, None)) is not None:
                action(reactions, id_, content)
                last_identifier = identifier
                last_content = content

    return reactions
