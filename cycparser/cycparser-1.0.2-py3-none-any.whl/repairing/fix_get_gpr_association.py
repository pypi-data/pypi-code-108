from __future__ import annotations

from typing import Dict, List, Set

from ..data import Enzyme, Reaction


def _get_monomers(
    cplx_or_monomer: str,
    complexes: Dict[str, Set[str]],
) -> Set[str]:
    result: Set[str] = set()
    if (components := complexes.get(cplx_or_monomer)) is not None:
        for component in components:
            if component in complexes:
                result.update(_get_monomers(component, complexes))
            else:
                result.add(component)
    else:  # doesn't necessarily need to be in monomers nor sequences
        result.add(cplx_or_monomer)
    return result


def get_gpr_associations(
    reactions: Dict[str, Reaction],
    enzymes: Dict[str, Enzyme],
    complexes: Dict[str, Set[str]],
) -> Dict[str, List[Set[str]]]:
    res: Dict[str, List[Set[str]]] = {}
    for name, reaction in reactions.items():
        for enzyme in reaction.enzrxns:
            if (cplx := enzymes[enzyme].cplx_or_monomer) is not None:
                res.setdefault(name, []).append(_get_monomers(cplx, complexes))
    return res
