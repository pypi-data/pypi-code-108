from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from ..data import Result
from .compounds import parse_compounds
from .enzymes import parse_enzymes
from .monomer_annotation import parse_monomer_annotation
from .monomer_sequences import parse_sequences
from .protein_complexes import parse_complexes
from .reactions import parse_reactions

__all__ = [
    "parse_pgdb",
    "parse_compounds",
    "parse_enzymes",
    "parse_monomer_annotation",
    "parse_complexes",
    "parse_reactions",
    "parse_sequences",
]


def remove_top_comments(file: List[str]) -> List[str]:
    """Remove the metainformation from a pgdb file."""
    for i, line in enumerate(file):
        if line.startswith("UNIQUE-ID"):
            return file[i:]
    return file


def read_file(path: Path) -> List[str]:
    try:
        with open(path, encoding="ISO-8859-14") as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def read_file_and_remove_comments(path: Path) -> List[str]:
    """Read the file and remove metainformation."""
    return remove_top_comments(read_file(path))


def parse_pgdb(path: Path, type_map: Dict[str, str] | None = None) -> Result:
    if type_map is None:
        type_map = {}

    return Result(
        compounds=parse_compounds(read_file_and_remove_comments(path / "compounds.dat"), type_map),
        reactions=parse_reactions(read_file_and_remove_comments(path / "reactions.dat"), type_map),
        monomer_annotation=parse_monomer_annotation(read_file_and_remove_comments(path / "genes.dat")),
        complexes=parse_complexes(read_file_and_remove_comments(path / "proteins.dat")),
        enzymes=parse_enzymes(read_file_and_remove_comments(path / "enzrxns.dat")),
        sequences=parse_sequences(iter(read_file(path / "protseq.fsa"))),
    )
