from __future__ import annotations

import copy
import itertools as it
from typing import Dict, List

from ..data import Compound, Reaction
from ..utils import reaction_is_bad


def _get_compound_variants(
    cpds: Dict[str, float],
    cpd_types: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    return {cpd: cpd_types[cpd] for cpd in cpds if cpd in cpd_types}


def _get_reaction_variant(
    rxn: Reaction,
    compound_map: dict[str, str],
    count: int,
) -> Reaction:
    local = copy.copy(rxn)
    local.substrates = {compound_map.get(k, k): v for k, v in local.substrates.items()}
    local.products = {compound_map.get(k, k): v for k, v in local.products.items()}
    local.substrate_compartments = {
        compound_map.get(k, k): v for k, v in local.substrate_compartments.items()
    }
    local.product_compartments = {compound_map.get(k, k): v for k, v in local.product_compartments.items()}
    local.id = f"{local.id}__var__{count}"
    local._var = count
    return local


def fix_create_reaction_variants(
    rxns: Dict[str, Reaction],
    cpds: Dict[str, Compound],
    compound_types: Dict[str, List[str]],
) -> Dict[str, Reaction]:
    """Create all mass and charge balanced reaction variants of reactions containing compound classes."""
    new_rxns = {}
    for rxn_id, rxn in rxns.items():
        count = 0
        substrate_variants = _get_compound_variants(rxn.substrates, compound_types)
        product_variants = _get_compound_variants(rxn.products, compound_types)

        variants = {**substrate_variants, **product_variants}
        if len(variants) == 0:
            new_rxns[rxn_id] = rxn
        else:
            for new_cpds, old_cpds in zip(
                it.product(*variants.values()),
                it.repeat(variants.keys()),
            ):
                compound_map = dict(zip(old_cpds, new_cpds))
                new_rxn = _get_reaction_variant(rxn, compound_map, count)
                # Performance improvement: filter garbage reactions already here
                if reaction_is_bad(new_rxn, cpds):
                    continue
                new_rxns[new_rxn.id] = new_rxn
                count += 1
    return new_rxns
