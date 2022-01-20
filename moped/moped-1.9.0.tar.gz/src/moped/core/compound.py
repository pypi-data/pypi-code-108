"""Compound abstraction."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

__all__ = ["Compound"]


@dataclass
class Compound:
    base_id: str
    compartment: str
    id: str = ""
    formula: Dict[str, float] = field(default_factory=dict)
    charge: int | None = None
    name: str | None = None
    gibbs0: float | None = None
    smiles: str | None = None
    database_links: Dict[str, Set[str]] = field(default_factory=dict)
    types: List[str] = field(default_factory=list)
    in_reaction: Set[str] = field(default_factory=set)

    def __hash__(self) -> int:
        """Hash the compound id."""
        return hash(self.id)

    def formula_to_string(self) -> str:
        """Create a string variant of the formula dict.

        Examples
        --------
        >>> Compound(formula={"C": 1, "H": 1}).formula_to_string()
        "C1H1"

        Returns
        -------
        formula_string: str
            The compound formula as a string representation
        """
        return "".join([str(k) + str(v) for k, v in self.formula.items()])
