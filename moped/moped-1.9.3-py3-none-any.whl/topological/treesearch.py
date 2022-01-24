"""Interface to tree search algorithms."""
from __future__ import annotations

from queue import LifoQueue, Queue
from typing import TYPE_CHECKING, Dict, Iterable, List, Tuple, cast

from typing_extensions import Literal

if TYPE_CHECKING:
    from ..core.model import Model

__all__ = ["metabolite_tree_search"]


def _deconstruct_path(
    end: str, parents: Dict[str, Tuple[str | None, str | None]]
) -> Tuple[List[str], List[str]]:
    """Deconstruct the path taken."""
    met, rec = parents[end]
    mets = [met]
    recs = [rec]
    while True:
        met, rec = parents[cast(str, met)]
        if met is not None:
            recs.append(rec)
            mets.append(met)
        else:
            return cast(List[str], mets[::-1] + [end]), cast(List[str], recs[::-1])


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


def _add_metabolite(
    child_metabolite: str,
    parent_metabolite: str,
    reaction_id: str,
    parents: Dict[str, Tuple[str | None, str | None]],
    Q: LifoQueue | Queue,
) -> None:
    if child_metabolite not in parents:
        parents[child_metabolite] = parent_metabolite, reaction_id
        Q.put(child_metabolite)


def metabolite_tree_search(
    model: Model,
    start_compound_id: str,
    end_compound_id: str,
    max_iterations: int,
    ignored_reaction_ids: Iterable[str] | None,
    ignored_compound_ids: Iterable[str] | None,
    search_type: Literal["breadth-first", "depth-first"],
) -> Tuple[List[str], List[str]]:
    """Do a tree search to find the shortest connection between two compounds.

    Parameters
    ----------
    start_compound_id : str
    end_compound_id : str
    max_iterations : int
    ignored_reaction_ids : iterable
    ignored_compound_ids : iterable
    search_type : str, {breadth-first, depth-first}
    """
    model = model.copy()
    for i in [start_compound_id, end_compound_id]:
        if i not in model.compounds:
            raise KeyError(f"Could not find compound {i}")
    ignored_reaction_ids = set() if ignored_reaction_ids is None else set(ignored_reaction_ids)
    ignored_compound_ids = set() if ignored_compound_ids is None else set(ignored_compound_ids)
    cofactors = set(model.get_weak_cofactors()) ^ set(model.get_strong_cofactors())

    reactions = split_stoichiometries(model)
    for i in ignored_reaction_ids:
        model.remove_reaction(reaction_id=i)

    if search_type == "breadth-first":
        Q: Queue | LifoQueue = Queue()  # FIFO Queue
    elif search_type == "depth-first":
        Q = LifoQueue()
    else:
        raise ValueError("Unknown search type, choose from {breadth-first, depth-first}")
    Q.put(start_compound_id)
    parents: Dict[str, Tuple[str | None, str | None]] = {
        k: (None, None) for k in (cofactors ^ {start_compound_id} ^ ignored_compound_ids)
    }  # Parent metabolites and reactions of discovered metabolites
    n = 0

    while not Q.empty():
        substrate_id = Q.get()
        if substrate_id == end_compound_id:
            return _deconstruct_path(end_compound_id, parents)

        for reaction_id in model.compounds[substrate_id].in_reaction:
            reaction = reactions[reaction_id]
            if substrate_id in reaction["substrates"]:
                for product_id in reaction["products"]:
                    _add_metabolite(product_id, substrate_id, reaction_id, parents, Q)
        n += 1
        if n == max_iterations:
            raise ValueError("Exceeded max iterations")
    else:
        raise ValueError("Could not find a solution")
