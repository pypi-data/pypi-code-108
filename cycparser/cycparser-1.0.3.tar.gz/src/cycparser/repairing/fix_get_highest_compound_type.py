from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from ..data import Compound


def get_highest_compound_type(compounds: Dict[str, Compound]) -> Dict[str, List[str]]:
    """Return (type: list(cpds)) dictionary.

    Only uses the highest-level type
    """
    types = defaultdict(list)
    for id_, cpd in compounds.items():
        if bool(cpd.types):
            # Only use highest level
            types[cpd.types[-1] + "_c"].append(id_)
    return dict(types)
