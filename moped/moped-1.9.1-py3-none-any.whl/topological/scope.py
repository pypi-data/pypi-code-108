"""Scope algorithm interace."""
from __future__ import annotations

import itertools
import sys
from collections.abc import Iterable
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, Dict, Set, Tuple

if TYPE_CHECKING:
    from ..core.model import Model

__all__ = [
    "scope",
    "multiple_scopes",
]


def split_stoichiometries(
    model: Model,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Split reaction stoichiometries into substrates and products.

    This is done to have the sets of either substrates and products
    to run the scope algorithm smoothly, e.g. comparing if substrates
    are a subset of the seed.

    Parameters
    ----------
    model: moped.Model

    Returns
    -------
    reations: dict
        Mapping of reaction ids to their substrates and products
    """
    reactions = {}
    for reaction_id, rxn in model.reactions.items():
        # Exclude medium reactions
        if len(rxn.stoichiometries) == 1:
            continue
        substrates, products = rxn.split_stoichiometries()
        reactions[reaction_id] = {
            "substrates": substrates,
            "products": products,
        }
    return reactions


def _create_seed_set(seed: str | Iterable[str], model: Model, include_weak_cofactors: bool) -> Set[str]:
    """Check the user seed input and unify it to be a set.

    Parameters
    ----------
    seed: str, Iterable(str)
    model: moped.Model
    include_weak_cofactors: bool
        Whether to include the weak cofactor of each cofactor pair
        defined in Model.cofactor_pairs.
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
        seed = seed.union(set(model.get_weak_cofactor_duplications()))
    return seed


def _scope(
    seed: str | Iterable[str],
    model: Model,
    reactions: Dict[str, Dict[str, Dict[str, float]]],
    include_weak_cofactors: bool,
    return_lumped_results: bool,
) -> Tuple[Set[str], Set[str]] | Tuple[list[Set[str]], list[Set[str]]]:
    """Run the scope algorithm.

    This function is called by both scope and multiple_scopes to actually run
    the algorithm.

    Parameters
    ----------
    seed: set
    model: moped.Model
    reactions: dict
        Mapping of reaction id to reactions substrates and products
    include_weak_cofactors: bool
        Whether to include the weak cofactor of each cofactor pair
        defined in Model.cofactor_pairs in the seed
    return_lumped_results: bool
        Whether to return the results separated by the simulation
        round or whether all the rounds should be lumped together.

    Returns
    -------
    scope_reactions: list(set) or set
    scope_compounds: list(set) or set
    """
    seed = _create_seed_set(seed=seed, model=model, include_weak_cofactors=include_weak_cofactors)
    all_compounds = seed.copy()
    scope_reactions = []
    scope_compounds = []
    possible_reactions = set(reactions)
    while True:
        new_reactions: Set[str] = set()
        new_compounds: Set[str] = set()
        reactions_to_remove = set()
        for reaction in possible_reactions:
            if set(reactions[reaction]["substrates"]).issubset(all_compounds):
                reactions_to_remove.add(reaction)
                new_reactions.add(reaction)
                new_compounds = new_compounds.union(set(reactions[reaction]["products"]))
        if len(new_reactions) > 0:
            # Remove duplicate compounds
            new_compounds = new_compounds.difference(all_compounds)
            scope_reactions.append(new_reactions)
            scope_compounds.append(new_compounds)
            # Update iterables
            all_compounds = all_compounds.union(new_compounds)
            possible_reactions = possible_reactions.difference(reactions_to_remove)
        else:
            if return_lumped_results:
                return (
                    set(itertools.chain.from_iterable(scope_reactions)),
                    set(itertools.chain.from_iterable(scope_compounds)),
                )
            return scope_reactions, scope_compounds


def scope(
    model: Model,
    seed: Iterable[str],
    include_weak_cofactors: bool,
    return_lumped_results: bool,
) -> Tuple[Set[str], Set[str]] | Tuple[list[Set[str]], list[Set[str]]]:
    """Run the scope algorithm.

    Parameters
    ----------
    seed: set
    model: moped.Model
    include_weak_cofactors: bool
        Whether to include the weak cofactor of each cofactor pair
        defined in Model.cofactor_pairs in the seed
    return_lumped_results: bool
        Whether to return the results separated by the simulation
        round or whether all the rounds should be lumped together.

    Raises
    ------
    ValueError
        If initial_seed is not str or List[str]
    """
    return _scope(
        seed=seed,
        model=model,
        reactions=split_stoichiometries(model),
        include_weak_cofactors=include_weak_cofactors,
        return_lumped_results=return_lumped_results,
    )


def multiple_scopes(
    model: Model,
    seeds: Iterable[Iterable[str]],
    include_weak_cofactors: bool,
    return_lumped_results: bool,
    multiprocessing: bool,
) -> Dict[tuple, Tuple[Set[str], Set[str]] | Tuple[list[Set[str]], list[Set[str]]]]:
    """Run the scope algorithm for multiple seeds.

    Parameters
    ----------
    seed: set
    model: moped.Model
    include_weak_cofactors: bool
        Whether to include the weak cofactor of each cofactor pair
        defined in Model.cofactor_pairs in the seed
    return_lumped_results: bool
        Whether to return the results separated by the simulation
        round or whether all the rounds should be lumped together.
    multiprocessing: bool
        Whether to utilize multiple processes for the calculation.
        This is always disabled for Windows os, as the multiprocessing
        tends to misbehave in those cases

    Raises
    ------
    ValueError
        If initial_seed is not str or List[str]

    Returns
    -------
    seeds: dict
        Dict mapping the seeds against the results. See return_lumped_results
        for the exact output format.
    """
    seeds_normalized = [tuple(i) for i in seeds]
    reactions = split_stoichiometries(model)
    partial_scope = partial(
        _scope,
        model=model,
        reactions=reactions,
        include_weak_cofactors=include_weak_cofactors,
        return_lumped_results=return_lumped_results,
    )
    if not multiprocessing or sys.platform in ["win32", "cygwin"]:
        return dict(zip(seeds_normalized, map(partial_scope, seeds)))
    else:
        pool = Pool(processes=cpu_count())
        res = dict(zip(seeds_normalized, pool.map(partial_scope, seeds)))
        pool.close()
        return res
