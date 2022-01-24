from __future__ import annotations

import copy
import itertools as it
import re
import warnings
from typing import Dict

from ..data import Compound, Reaction


def _map_compartment_to_model_compartments(
    *,
    compartment: str,
    compartment_map: Dict[str, str],
) -> str:
    if compartment in compartment_map:
        return compartment_map[compartment]
    warnings.warn(f"Unknown compartment {compartment}. Mapping to cytosol")
    return compartment_map["CYTOSOL"]


def _add_moped_compartment_suffix(
    *,
    object_id: str,
    compartment: str,
    compartment_suffixes: Dict[str, str],
) -> str:
    return f"{object_id}_{compartment_suffixes[compartment]}"


def _split_location(*, location: str, compartment_map: Dict[str, str]) -> Dict[str, str]:
    """Split concatented rxn-location strings.

    Example input:

    CCO-EXTRACELLULAR-CCO-CYTOSOL
    CCO-PM-BAC-NEG
    In some cases only one is given, even if a transporter is
    described. In that case, the in-compartment is always the cytosol
    """
    split = re.split(r"(\-?CCO\-)", location)
    try:
        out_, in_ = split[2::2]
    except ValueError:
        out_ = split[2]
        in_ = "CYTOSOL"
    return {
        "CCO-OUT": _map_compartment_to_model_compartments(compartment=out_, compartment_map=compartment_map),
        "CCO-IN": _map_compartment_to_model_compartments(compartment=in_, compartment_map=compartment_map),
    }


def _add_compartment_compound_variant(
    *,
    cpd_id: str,
    compartment: str,
    compounds: Dict[str, Compound],
    compartment_suffixes: Dict[str, str],
) -> str:
    """Add a copy of the compound and change the suffix."""
    new_id = _add_moped_compartment_suffix(
        object_id=compounds[cpd_id].base_id,
        compartment=compartment,
        compartment_suffixes=compartment_suffixes,
    )
    new_cpd = copy.copy(compounds[cpd_id])
    new_cpd.id = new_id
    new_cpd.compartment = compartment
    compounds[new_id] = new_cpd
    return new_id


def _all_compartments_match(*, rxn: Reaction, compartment: str) -> bool:
    return all(
        i == compartment
        for i in it.chain(
            rxn.substrate_compartments.values(),
            rxn.product_compartments.values(),
        )
    )


def _create_compartment_reaction(
    *,
    rxn: Reaction,
    compartment: str,
    compounds: Dict[str, Compound],
    compartment_suffixes: Dict[str, str],
) -> Reaction:
    local = copy.copy(rxn)
    local.substrates = {
        _add_compartment_compound_variant(
            cpd_id=k,
            compartment=compartment,
            compounds=compounds,
            compartment_suffixes=compartment_suffixes,
        ): v
        for k, v in local.substrates.items()
    }
    local.products = {
        _add_compartment_compound_variant(
            cpd_id=k,
            compartment=compartment,
            compounds=compounds,
            compartment_suffixes=compartment_suffixes,
        ): v
        for k, v in local.products.items()
    }
    local.id = _add_moped_compartment_suffix(
        object_id=local.id,
        compartment=compartment,
        compartment_suffixes=compartment_suffixes,
    )
    local.compartment = compartment
    return local


def _get_sides(side: str, location: str, compartment_map: Dict[str, str]) -> Dict[str, str]:
    if "-CCO-" in location:
        return _split_location(location=location, compartment_map=compartment_map)
    else:
        return {
            side: _map_compartment_to_model_compartments(
                compartment=location[4:],
                compartment_map=compartment_map,
            )
        }


def _create_single_compartment_variant(
    *,
    rxn: Reaction,
    location: str,
    side: str,
    compounds: Dict[str, Compound],
    compartment_map: Dict[str, str],
    compartment_suffixes: Dict[str, str],
) -> Reaction:
    sides = _get_sides(side, location, compartment_map)
    return _create_compartment_reaction(
        rxn=rxn,
        compartment=sides[side],
        compounds=compounds,
        compartment_suffixes=compartment_suffixes,
    )


def _create_transmembrane_reaction(
    *,
    rxn: Reaction,
    sides: Dict[str, str],
    compounds: Dict[str, Compound],
    compartment_suffixes: Dict[str, str],
) -> Reaction:
    local = copy.copy(rxn)
    local.substrates = {
        _add_compartment_compound_variant(
            cpd_id=k,
            compartment=sides[local.substrate_compartments[k]],
            compounds=compounds,
            compartment_suffixes=compartment_suffixes,
        ): v
        for k, v in local.substrates.items()
    }
    local.products = {
        _add_compartment_compound_variant(
            cpd_id=k,
            compartment=sides[local.product_compartments[k]],
            compounds=compounds,
            compartment_suffixes=compartment_suffixes,
        ): v
        for k, v in local.products.items()
    }
    # Add suffix to reaction name
    in_suffix = _add_moped_compartment_suffix(
        object_id="",
        compartment=sides["CCO-IN"],
        compartment_suffixes=compartment_suffixes,
    )
    out_suffix = _add_moped_compartment_suffix(
        object_id="",
        compartment=sides["CCO-OUT"],
        compartment_suffixes=compartment_suffixes,
    )
    # Add suffix to reaction name
    local.id += in_suffix + out_suffix
    local.compartment = (sides["CCO-IN"], sides["CCO-OUT"])
    local.transmembrane = True
    return local


def fix_create_compartment_variants(
    parse_reactions: Dict[str, Reaction],
    compounds: Dict[str, Compound],
    compartment_map: Dict[str, str],
    compartment_suffixes: Dict[str, str],
) -> Dict[str, Reaction]:
    """Fix issues with consistency of pgdbs when it comes to compartments.

    This maps the location information according to the compartment_map that
    was supplied. By default only CYTOSOL, PERIPLASM and EXTRACELLULAR are used.

    If no location is given, CCO-CYTOSOL is assumed for CCO-IN and CCO-EXTRACELLULAR
    for CCO-OUT. Accordingly transport reactions with no location are assumed to be
    CCO-EXTRACELLULAR-CCO-CYTOSOL.

    Notes
    -----
    CCO-EXTRACELLULAR-CCO-CYTOSOL means CCO-OUT means EXTRACELLULAR and CCO-IN means
    CYTOSOL, so the format is CCO-OUT-CCO-IN. No idea why.
    """
    new_reactions = {}
    for rxn in parse_reactions.values():
        if _all_compartments_match(rxn=rxn, compartment="CCO-IN"):
            if not bool(rxn.locations):
                rxn.locations = ["CCO-CYTOSOL"]
            for location in rxn.locations:
                local = _create_single_compartment_variant(
                    rxn=rxn,
                    location=location,
                    side="CCO-IN",
                    compounds=compounds,
                    compartment_map=compartment_map,
                    compartment_suffixes=compartment_suffixes,
                )
                new_reactions[local.id] = local
        elif _all_compartments_match(rxn=rxn, compartment="CCO-OUT"):
            if not bool(rxn.locations):
                rxn.locations = ["CCO-EXTRACELLULAR"]
            for location in rxn.locations:
                local = _create_single_compartment_variant(
                    rxn=rxn,
                    location=location,
                    side="CCO-OUT",
                    compounds=compounds,
                    compartment_map=compartment_map,
                    compartment_suffixes=compartment_suffixes,
                )
                new_reactions[local.id] = local
        else:
            if not bool(rxn.locations):
                rxn.locations = ["CCO-EXTRACELLULAR-CCO-CYTOSOL"]
            for location in rxn.locations:
                sides = _split_location(location=location, compartment_map=compartment_map)
                if sides["CCO-IN"] == sides["CCO-OUT"]:
                    local = _create_compartment_reaction(
                        rxn=rxn,
                        compartment=sides["CCO-OUT"],
                        compounds=compounds,
                        compartment_suffixes=compartment_suffixes,
                    )
                    new_reactions[local.id] = local
                else:
                    local = _create_transmembrane_reaction(
                        rxn=rxn,
                        sides=sides,
                        compounds=compounds,
                        compartment_suffixes=compartment_suffixes,
                    )
                    new_reactions[local.id] = local
    return new_reactions
