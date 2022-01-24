"""Gapfilling functions. Mostly a meneco interface."""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Iterable, List, cast

import pyasp
from __meneco__ import query, utils

if TYPE_CHECKING:
    from ..core.model import Model

__all__ = ["gapfilling"]


def model_to_termset(model: "Model", model_name: str) -> pyasp.TermSet:
    """Convert a moped model into a meneco termset.

    Parameters
    ----------
    model: moped.Model
    model_name: str

    Returns
    -------
    model_terms: pyasp.term.TermSet
        Converted model
    """
    model_terms = pyasp.TermSet()
    for reaction in model.reactions.values():
        model_terms.add(pyasp.Term("reaction", ['"' + reaction.id + '"', '"' + model_name + '"']))
        substrates, products = reaction.split_stoichiometries()
        for substrate in substrates:
            model_terms.add(
                pyasp.Term(
                    "reactant",
                    [
                        '"' + substrate + '"',
                        '"' + reaction.id + '"',
                        '"' + model_name + '"',
                    ],
                )
            )
        for product in products:
            model_terms.add(
                pyasp.Term(
                    "product",
                    [
                        '"' + product + '"',
                        '"' + reaction.id + '"',
                        '"' + model_name + '"',
                    ],
                )
            )
    return model_terms


def compound_id_to_term(compound_type: str, compound_id: str) -> pyasp.Term:
    """Convert a moped compound into a meneco termset.

    Parameters
    ----------
    compound_type: str
        E.g. reactant, product, target
    compound_id: str

    Returns
    -------
    compound_term: pyasp.Term
        Converted compound
    """
    return pyasp.Term(compound_type, ['"' + compound_id + '"'])


def compound_list_to_termset(compound_type: str, compound_iterable: Iterable[str]) -> pyasp.TermSet:
    """Convert a moped compound list into a meneco termset.

    Parameters
    ----------
    compound_type: str
        E.g. reactant, product, target
    compound_iterable: Iterable(str)

    Returns
    -------
    terms: pyasp.TermSet
        Converted compounds
    """
    terms = pyasp.TermSet()
    for compound_id in compound_iterable:
        terms.add(compound_id_to_term(compound_type, compound_id))
    return terms


def get_unproducible_compounds(
    model: pyasp.TermSet, targets: Iterable[str], seed: Iterable[str]
) -> pyasp.TermSet:
    """Get compounds that are not producible given the model and seed compounds.

    Parameters
    ----------
    model: pyasp.term.TermSet
    targets: Iterable(str)
        Compounds to be produced
    seed: Iterable(str)
        Compounds with which the algorithm starts

    Returns
    -------
    unproducible_compounds: pyasp.TermSet
    """
    return pyasp.TermSet(
        [
            compound_id_to_term("target", i.arg(0).strip('"'))
            for i in query.get_unproducible(model, targets, seed)
        ]
    )


def get_essential_reactions(
    model: pyasp.TermSet,
    database: pyasp.TermSet,
    seed: Iterable[str],
    producible: Iterable[str],
) -> pyasp.TermSet:
    """Get essential reactions to produce the producible reactions.

    Parameters
    ----------
    model: pyasp.term.TermSet
    database: pyasp.term.TermSet
        All possible reactions
    seed: Iterable(str)
        Compounds with which the algorithm starts
    producible: Iterable(str)
        Compounds that can be produced in the database

    Returns
    -------
    essential_reactions: pyasp.TermSet
        All reactions that are essential to produce the producible reactions
    """
    essential_reactions: pyasp.TermSet = pyasp.TermSet()
    for target in producible:
        single_target = pyasp.TermSet()
        single_target.add(target)
        essentials = query.get_intersection_of_completions(model, database, seed, single_target)
        essential_reactions = cast(pyasp.TermSet, essential_reactions.union(essentials))
    return essential_reactions


def term_to_str(term: pyasp.Term) -> str:
    """Convert a pyasp term to a Python string.

    Parameters
    ----------
    term: pyasp.Term

    Returns
    -------
    term_str: str
    """
    return term.arg(0).strip('"')  # type: ignore


def gapfilling(
    model: "Model",
    reference_model: "Model",
    seed: Iterable[str],
    targets: Iterable[str],
    include_weak_cofactors: bool = False,
    verbose: bool = False,
) -> List[str]:
    """Gap-filling using the meneco package.

    Parameters
    ----------
    model: moped.Model
    reference_model: moped.Model
    seed: List[str]
    targets: List[str]
    include_weak_cofactors: bool, optional
        Whether to include the weak cofactor duplications
    verbose: bool, optional
        Whether to print progress notifications

    Returns
    -------
    essential_reactions: List[str]
        The minimal amount of reactions required to reach all the targets
    """
    if isinstance(seed, str):
        seed = [seed]
    elif isinstance(seed, Iterable):
        if not all(isinstance(i, str) for i in seed):
            raise TypeError("Initial seed has to be str or Iterable[str]")
    else:
        raise TypeError("Initial seed has to be str or Iterable[str]")
    seed = set(seed)
    if include_weak_cofactors:
        seed = seed.union(set(reference_model.get_weak_cofactor_duplications()))

    for target in targets:
        if target not in reference_model.compounds:
            warnings.warn(f"Target {target} could not be found in the database")

    model_terms = model_to_termset(model, "draft")
    db_terms = model_to_termset(reference_model, "repair")

    seed = compound_list_to_termset("seed", seed)
    targets = compound_list_to_termset("target", targets)

    unproducible_model = get_unproducible_compounds(model_terms, targets, seed)
    if verbose:
        print(f"Searching for {[term_to_str(p) for p in unproducible_model]} in reference database")
    unproducible_database = get_unproducible_compounds(db_terms, targets, seed)
    producible = unproducible_model.difference(unproducible_database)

    if len(unproducible_database) > 0:
        warnings.warn(
            f"Could not produce {[term_to_str(p) for p in unproducible_database]} in reference database"
        )
        if verbose:
            print(f"Could produce {[term_to_str(p) for p in producible]} in reference database")
    else:
        if verbose:
            print("Could produce all compounds in reference database")

    essential_reactions = get_essential_reactions(model_terms, db_terms, seed, producible)
    if verbose:
        print(f"Found {len(essential_reactions)} essential reaction(s)")
    filled_model = pyasp.TermSet(model_terms.union(essential_reactions))
    utils.clean_up()

    # Get minimal solution
    min_models = query.get_minimal_completion_size(filled_model, db_terms, seed, producible)
    return [term_to_str(term) for term in min_models[0]]
