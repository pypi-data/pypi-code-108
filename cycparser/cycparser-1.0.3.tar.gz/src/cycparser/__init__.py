from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from .data import (
    Compound,
    Cyc,
    Enzyme,
    KineticData,
    Monomer,
    MonomerAnnotation,
    Reaction,
    Result,
)
from .defaults import COMPARTMENT_MAP, COMPARTMENT_SUFFIXES, MANUAL_ADDITIONS, TYPE_MAP
from .parsing import parse_pgdb
from .repairing import (
    fix_add_important_compounds,
    fix_create_compartment_variants,
    fix_create_reaction_variants,
    fix_filter_garbage_reactions,
    fix_set_reaction_stoichiometry,
    fix_unify_reaction_direction,
    get_gpr_associations,
    get_highest_compound_type,
    get_kinetic_data,
)

__all__ = [
    "repair",
    "parse_and_repair_pgdb",
    "Compound",
    "Cyc",
    "Enzyme",
    "KineticData",
    "Monomer",
    "MonomerAnnotation",
    "Reaction",
    "COMPARTMENT_MAP",
    "COMPARTMENT_SUFFIXES",
    "MANUAL_ADDITIONS",
    "TYPE_MAP",
]


def combine_sequence_and_annotation(
    sequences: Dict[str, str], annotation: Dict[str, MonomerAnnotation]
) -> Dict[str, Monomer]:
    return {
        k: Monomer(id=k, sequence=sequences[k], database_links=v.database_links)
        for k, v in annotation.items()
        if k in sequences
    }


def repair(
    parse_result: Result,
    compartment_map: Dict[str, str],
    manual_additions: Dict[str, Compound],
    compartment_suffixes: Dict[str, str],
) -> Cyc:
    compounds = parse_result.compounds
    reactions = parse_result.reactions
    monomer_annotation = parse_result.monomer_annotation
    complexes = parse_result.complexes
    enzymes = parse_result.enzymes
    sequences = parse_result.sequences

    monomers = combine_sequence_and_annotation(sequences, monomer_annotation)

    # Generate dervied data
    compound_types = get_highest_compound_type(compounds)
    gpr_annotations = get_gpr_associations(reactions, enzymes, complexes)
    kinetic_data = get_kinetic_data(reactions, enzymes)

    # Small fixes
    compounds = fix_add_important_compounds(compounds, manual_additions)
    reactions = fix_unify_reaction_direction(reactions)

    # Larger fixes
    reactions = fix_create_reaction_variants(reactions, compounds, compound_types)
    reactions = fix_filter_garbage_reactions(reactions, compounds)
    reactions = fix_create_compartment_variants(
        reactions,
        compounds,
        compartment_map,
        compartment_suffixes,
    )
    reactions = fix_set_reaction_stoichiometry(reactions)

    # Post fixing
    used_compartments: Set[str] = {i.compartment for i in compounds.values() if i.compartment is not None}
    compartments: Dict[str, str] = {i: compartment_suffixes[i] for i in used_compartments}
    return Cyc(compounds, reactions, compartments, gpr_annotations, kinetic_data, monomers)


def parse_and_repair_pgdb(
    pgdb_path: Path,
    compartment_map: Dict[str, str] | None = None,
    type_map: Dict[str, str] | None = None,
    manual_additions: Dict[str, Compound] | None = None,
    compartment_suffixes: Dict[str, str] | None = None,
) -> Cyc:
    if compartment_map is None:
        compartment_map = COMPARTMENT_MAP
    if type_map is None:
        type_map = TYPE_MAP
    if manual_additions is None:
        manual_additions = MANUAL_ADDITIONS
    if compartment_suffixes is None:
        compartment_suffixes = COMPARTMENT_SUFFIXES
    return repair(
        parse_pgdb(pgdb_path, type_map),
        compartment_map,
        manual_additions,
        compartment_suffixes,
    )
