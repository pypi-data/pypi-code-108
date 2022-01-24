from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

__all__ = ["Reaction"]

from .kinetic_data import KineticData


@dataclass
class Reaction:
    id: str
    compartment: str | Tuple[str, ...] | None = None
    stoichiometries: Dict[str, float] = field(default_factory=dict)
    bounds: Tuple[float, float] = (0, 1000)
    gibbs0: float | None = None
    ec: str | None = None
    types: List[str] = field(default_factory=list)
    pathways: Set[str] = field(default_factory=set)
    database_links: Dict[str, Set[str]] = field(default_factory=dict)
    gpr_annotation: List[Set[str]] = field(default_factory=list)
    kinetic_data: Dict[str, KineticData] = field(default_factory=dict)
    # sequences: Dict[str, str] = field(default_factory=dict)
    transmembrane: bool | None = None
    name: str | None = None
    base_id: str | None = None
    _var: int | None = None
    _gpa: int | None = None  # set only if reaction is found by blasting

    def __post_init__(self) -> None:
        if self.base_id is None:
            self.base_id = self.id

        if self.transmembrane is None:
            compound_compartments: set[str] = set()
            for i in self.stoichiometries:
                try:
                    compartment = i.rsplit("_", maxsplit=1)[1]
                except IndexError:
                    pass
                else:
                    compound_compartments.add(compartment)
            if len(compound_compartments) > 1:
                self.transmembrane = True
            else:
                self.transmembrane = False

    @property
    def reversible(self) -> bool:
        lb, ub = self.bounds
        return lb < 0 and ub > 0

    def __hash__(self) -> int:
        """Hash the compound id."""
        return hash(self.id)

    def split_stoichiometries(
        self,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Split the reaction stoichiometries into substrates and products.

        This is mostly used in structural analyses, such as the scope algorithm.

        Returns
        -------
        substrates: dict(str: float)
        products: dict(str: float)
        """
        substrates: dict[str, float] = {}
        products: dict[str, float] = {}
        for k, v in self.stoichiometries.items():
            if v < 0:
                substrates[k] = v
            else:
                products[k] = v
        return substrates, products

    def replace_compound(self, old_compound: str, new_compound: str) -> None:
        """Replace a compound with another, keeping the stoichiometries.

        Parameters
        ----------
        old_compound : str
            Id of the compound to be replaced
        new_compound : str
            Id of the replacing compound
        """
        stoich = self.stoichiometries.pop(old_compound)
        self.stoichiometries[new_compound] = stoich

    def reverse_stoichiometry(self) -> None:
        """Reverses the stoichiometry of the reaction.

        This also reverses the bounds and gibbs0
        """
        self.stoichiometries = {k: -v for k, v in self.stoichiometries.items()}
        if self.gibbs0 is not None:
            self.gibbs0 = -self.gibbs0
        if self.bounds is not None:
            self.bounds = (-self.bounds[1], -self.bounds[0])

    def make_reversible(self) -> None:
        """Make the reaction reversible."""
        lb, ub = self.bounds
        # Check if it is not really irreversible in the first place
        if lb < 0 and ub > 0:
            pass
        elif lb < 0:
            self.bounds = (lb, -lb)
        else:
            self.bounds = (-ub, ub)

    def make_irreversible(self) -> None:
        """Make the reaction irreversible."""
        lb, ub = self.bounds
        if lb < 0 and ub > 0:
            self.bounds = (0, ub)
        # Maybe it was annotated wrong
        elif ub > 0:
            self.bounds = (0, ub)
        else:
            self.bounds = (lb, 0)
