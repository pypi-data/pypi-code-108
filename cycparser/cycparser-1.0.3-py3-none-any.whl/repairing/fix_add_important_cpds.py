from __future__ import annotations

from typing import Dict

from ..data import Compound


def fix_add_important_compounds(
    compounds: Dict[str, Compound],
    manual_additions: Dict[str, Compound],
) -> Dict[str, Compound]:
    compounds.update(manual_additions)
    return compounds
