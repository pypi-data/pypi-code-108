from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

__all__ = [
    "Monomer",
    "MonomerAnnotation",
    "Compound",
    "Reaction",
    "Enzyme",
]


@dataclass
class Compound:
    id: str
    base_id: str
    charge: int = 0
    compartment: str = "CYTOSOL"
    smiles: str | None = None
    name: str | None = None
    gibbs0: float | None = None
    types: List[str] = field(default_factory=list)
    formula: Dict[str, float] = field(default_factory=dict)
    database_links: Dict[str, Set[str]] = field(default_factory=dict)


@dataclass
class Reaction:
    id: str
    base_id: str
    bounds: Tuple[float, float] = (0, 0)
    name: str | None = None
    ec: str | None = None
    gibbs0: float | None = None
    direction: str = "LEFT-TO-RIGHT"
    reversible: bool = False
    transmembrane: bool = False
    substrates: Dict[str, float] = field(default_factory=dict)
    substrate_compartments: Dict[str, str] = field(default_factory=dict)
    products: Dict[str, float] = field(default_factory=dict)
    product_compartments: Dict[str, str] = field(default_factory=dict)
    types: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    pathways: Set[str] = field(default_factory=set)
    enzrxns: Set[str] = field(default_factory=set)
    database_links: Dict[str, Set[str]] = field(default_factory=dict)
    _var: int | None = None
    # Later additions
    compartment: str | Tuple[str, str] | None = None
    stoichiometries: Dict[str, float] = field(default_factory=dict)


@dataclass
class MonomerAnnotation:
    id: str
    product: str | None = None  # Later used as id
    database_links: Dict[str, Set[str]] = field(default_factory=dict)


@dataclass
class Monomer:
    id: str
    sequence: str
    database_links: Dict[str, Set[str]] = field(default_factory=dict)


@dataclass
class KineticData:
    kcat: Dict[str, float] = field(default_factory=dict)
    km: Dict[str, float] = field(default_factory=dict)
    vmax: Dict[str, float] = field(default_factory=dict)


@dataclass
class Enzyme:
    id: str
    cplx_or_monomer: str | None = None
    kinetic_data: KineticData = field(default_factory=KineticData)


@dataclass
class Result:
    compounds: Dict[str, Compound]
    reactions: Dict[str, Reaction]
    monomer_annotation: Dict[str, MonomerAnnotation]
    complexes: Dict[str, Set[str]]
    enzymes: Dict[str, Enzyme]
    sequences: Dict[str, str]


@dataclass
class Cyc:
    compounds: Dict[str, Compound]
    reactions: Dict[str, Reaction]
    compartments: Dict[str, str]
    gpr_annotations: Dict[str, List[Set[str]]]  # rxn: [monomer*]
    kinetic_data: Dict[str, Dict[str, KineticData]]  # rxn: enzyme: data
    monomers: Dict[str, Monomer]  # monomer: sequence / annotation
