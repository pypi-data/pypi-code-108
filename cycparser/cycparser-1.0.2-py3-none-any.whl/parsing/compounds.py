from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Dict, Iterable

from ..data import Compound
from .shared import (
    MALFORMED_LINE_STARTS,
    _add_database_link,
    _add_type,
    _set_gibbs0,
    _set_name,
)

__all__ = ["parse_compounds"]

logger = logging.getLogger(__name__)
Action = Callable[[Dict[str, Any], str, str], None]


def _set_atom_charges(compounds: Dict[str, Compound], id_: str, content: str) -> None:
    try:
        compounds[id_].charge += int(content[1:-1].split()[-1])
    except ValueError:  # conversion failed
        pass


def _set_chemical_formula(compounds: Dict[str, Compound], id_: str, content: str) -> None:
    atom, count = content[1:-1].split(" ")
    try:
        compounds[id_].formula[atom] = int(count)
    except ValueError:  # conversion failed
        pass


def _set_smiles(compounds: Dict[str, Compound], id_: str, content: str) -> None:
    compounds[id_].smiles = content


def parse_compounds(
    file: Iterable[str],
    type_map: dict[str, str],
    actions: Dict[str, Action] | None = None,
    db_to_resource: dict[str, str] | None = None,
) -> Dict[str, Compound]:
    if db_to_resource is None:
        db_to_resource = {
            "BIGG": "bigg.metabolite",
            "BRENDA-COMPOUND": "brenda",
            "CAS": "cas",
            "CHEBI": "CHEBI",
            "CHEMSPIDER": "CHEMSPIDER",
            "DRUGBANK": "drugbank",
            # "ECOCYC": None,
            "HMDB": "HMDB",
            "KEGG": "kegg.compound",
            "KEGG-GLYCAN": "kegg.glycan",
            "KNAPSACK": "knapsack",
            # "LIGAND-CPD": None,
            # "LIPID_MAPS": None,
            # "MEDIADB": None,
            "METABOLIGHTS": "metabolights",
            "METANETX": "metanetx.chemical",
            # "NCI": None,
            "PUBCHEM": "pubchem.compound",
            "PUBCHEM-SID": "pubchem.substance",
            "REACTOME-CPD": "reactome",
            # "REFMET": None,
            "SEED": "seed.compound",
            "UM-BBD-CPD": "umbbd.compound",
        }
    if actions is None:
        actions = {
            "TYPES": partial(_add_type, type_map=type_map),
            "COMMON-NAME": _set_name,
            "ATOM-CHARGES": _set_atom_charges,
            "CHEMICAL-FORMULA": _set_chemical_formula,
            "DBLINKS": partial(_add_database_link, db_to_resource=db_to_resource),
            "GIBBS-0": _set_gibbs0,
            "SMILES": _set_smiles,
        }

    compounds: Dict[str, Compound] = {}
    id_ = ""
    for line in file:
        if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
            continue
        try:
            identifier, content = line.rstrip().split(" - ", maxsplit=1)
        except ValueError:
            logger.info(f"Malformed line in compoudns.dat: {line}")
            continue

        if identifier == "UNIQUE-ID":
            base_id = content
            id_ = content + "_c"
            compounds[id_] = Compound(
                id=id_,
                base_id=base_id,
                compartment="CYTOSOL",
                database_links={
                    "biocyc": set([base_id]),
                    "metacyc.compound": set([base_id]),
                },
            )
        else:
            if (action := actions.get(identifier, None)) is not None:
                action(compounds, id_, content)
    return compounds
