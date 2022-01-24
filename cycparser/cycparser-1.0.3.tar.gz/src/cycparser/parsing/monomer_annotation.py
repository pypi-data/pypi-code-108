from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Dict, Iterable

from ..data import MonomerAnnotation
from .shared import MALFORMED_LINE_STARTS, _add_database_link

__all__ = ["parse_monomer_annotation"]

logger = logging.getLogger(__name__)
Action = Callable[[Any, Any, Any], None]


def _set_gene_product(genes: Dict[str, MonomerAnnotation], id_: str, product: str) -> None:
    genes[id_].product = product


def parse_monomer_annotation(
    file: Iterable[str],
    actions: Dict[str, Action] | None = None,
    db_to_resource: dict[str, str] | None = None,
) -> Dict[str, MonomerAnnotation]:
    if db_to_resource is None:
        db_to_resource = {
            "ARRAYEXPRESS": "arrayexpress",
            "ASAP": "asap",
            "CGD": "cgd",
            "CGSC": "cgsc",
            "ECHOBASE": "echobase",
            "ENSEMBL": "ensembl",
            "ENSEMBLGENOMES-GN": "ensembl",
            "ENSEMBLGENOMES-TR": "ensembl",
            "GENECARDS": "genecards",
            "GO": "GO",
            "GOA": "goa",
            "GRAMENE": "gramene.gene",
            "IMG": "img.gene",
            "INTERPRO": "interpro",
            "KEGG": "kegg.genes",
            "MAIZEGDB": "maizegdb.locus",
            "MGI": "MGI",
            "MIM": "mim",
            "NCBI-GENE": "ncbigene",
            "PDB": "pdb",
            "PHYTOZOME": "phytozome.locus",
            "PID": "pid.pathway",
            "REFSEQ": "refseq",
            "SGD": "sgb",
            "SGN": "sgn",
            "STRING": "string",
            "SUBTILIST": "subtilist",
            "SUBTIWIKI": "subtiwiki",
            "TAIR": "tair.gene",
            "UNIGENE": "unigene",
            "UNIPROT": "uniprot",
        }
    if actions is None:
        actions = {
            "DBLINKS": partial(_add_database_link, db_to_resource=db_to_resource),
            "PRODUCT": _set_gene_product,
        }

    genes: Dict[str, MonomerAnnotation] = {}
    id_ = ""
    for line in file:
        if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
            continue
        try:
            identifier, content = line.rstrip().split(" - ", maxsplit=1)
        except ValueError:
            logger.info(f"Malformed line in genes.dat: {line}")
            continue

        if identifier == "UNIQUE-ID":
            id_ = content
            genes[content] = MonomerAnnotation(id=content)
        else:
            if (action := actions.get(identifier, None)) is not None:
                action(genes, id_, content)
    return {
        product: MonomerAnnotation(id=product, database_links=i.database_links)
        for i in genes.values()
        if (product := i.product) is not None
    }
