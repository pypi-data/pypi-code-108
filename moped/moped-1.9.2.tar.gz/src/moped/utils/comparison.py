from __future__ import annotations

from functools import singledispatch
from typing import Any, Dict, Optional, Tuple

from cobra import Metabolite as CobraMetabolite
from cobra import Reaction as CobraReaction

from ..core.compound import Compound
from ..core.model import Model
from ..core.reaction import Reaction

__all__ = ["difference"]


@singledispatch
def difference(x: Any, y: Any) -> Any:
    raise NotImplementedError(x.__class__.__name__)


@difference.register
def _difference_none(x: None, y: None) -> None:
    return None


@difference.register
def _difference_str(x: str, y: str) -> Optional[Tuple[str, Optional[str]]]:
    if y is None:
        return (x, None)
    elif not isinstance(y, str):
        # raise TypeError(f"Type {y.__class__.__name__} is not a str")
        print(f"Type {y.__class__.__name__} is not a str")
        return (x, None)
    if x != y:
        return (x, y)
    return None


@difference.register
def _difference_int(x: int, y: int) -> Optional[Tuple[int, Optional[int]]]:
    if y is None:
        return (x, None)
    elif not isinstance(y, (int, float)):
        # raise TypeError(f"Type {y.__class__.__name__} is not a int")
        print(f"Type {y.__class__.__name__} is not a int")
        return (x, None)
    if x != y:
        return (x, y)
    return None


@difference.register
def _difference_float(x: float, y: float) -> Optional[Tuple[float, Optional[float]]]:
    if y is None:
        return (x, None)
    elif not isinstance(y, float):
        # raise TypeError(f"Type {y.__class__.__name__} is not a float")
        print(f"Type {y.__class__.__name__} is not a float")
        return (x, None)
    if x != y:
        return (x, y)
    return None


@difference.register
def _difference_set(x: set, y: set) -> set:
    if y is None:
        return x
    elif not isinstance(y, set):
        # raise TypeError(f"Type {y.__class__.__name__} is not a set")
        print(f"Type {y.__class__.__name__} is not a set")
        return x
    return x.symmetric_difference(y)


@difference.register
def _difference_list(x: list, y: list) -> list[Any]:
    if y is None:
        return x
    elif not isinstance(y, list):
        # raise TypeError(f"Type {y.__class__.__name__} is not a list")
        print(f"Type {y.__class__.__name__} is not a list")
        return x
    return [d for x, y in zip(x, y) if bool(d := difference(x, y))]


@difference.register
def _difference_tuple(x: tuple, y: tuple) -> list[Any]:
    if y is None:
        return list(x)
    elif not isinstance(y, tuple):
        raise TypeError(f"Type {y.__class__.__name__} is not a tuple")
    return [d for x, y in zip(x, y) if bool(d := difference(x, y))]


@difference.register
def _difference_dict(x: dict, y: dict) -> dict:
    if y is None:
        return x
    elif not isinstance(y, dict):
        raise TypeError(f"Type {y.__class__.__name__} is not a dict")
    return {k: v for k in x if bool(v := difference(x[k], y.get(k, None)))}


@difference.register
def _difference_compound(x: Compound, y: Compound) -> Dict[str, Any]:
    if not isinstance(y, Compound):
        raise TypeError("Types of x and y need to match")
    return {i: d for i in x.__dict__ if bool(d := difference(getattr(x, i), getattr(y, i)))}


@difference.register
def _difference_reaction(x: Reaction, y: Reaction) -> Dict[str, Any]:
    if not isinstance(y, Reaction):
        raise TypeError("Types of x and y need to match")
    return {i: d for i in x.__dict__ if bool(d := difference(getattr(x, i), getattr(y, i)))}


@difference.register
def _difference_model(x: Model, y: Model) -> Dict[str, Any]:
    if not isinstance(y, Model):
        raise TypeError("Types of x and y need to match")
    return {i: d for i in x.__dict__ if bool(d := difference(getattr(x, i), getattr(y, i)))}


@difference.register
def _difference_frozenset(x: frozenset, y: frozenset) -> frozenset:
    if y is None:
        return x
    elif not isinstance(y, frozenset):
        print(f"Type {y.__class__.__name__} is not a frozenset")
        return x
    return x.symmetric_difference(y)


@difference.register
def _difference_cobra_metabolite(x: CobraMetabolite, y: CobraMetabolite) -> list[Any]:
    fields = (
        "id",
        "name",
        "notes",
        "annotation",
        # "model",
        "formula",
        "compartment",
        "charge",
    )
    result = [diff for field in fields if bool(diff := difference(getattr(x, field), getattr(y, field)))]
    if diff := difference({i.id for i in x.reactions}, {i.id for i in x.reactions}):
        result.append(diff)
    return result


@difference.register
def _difference_cobra_reaction(x: CobraReaction, y: CobraReaction) -> list[Any]:
    fields = (
        "id",
        "name",
        "notes",
        "annotation",
        "gene_reaction_rule",
        "subsystem",
        "genes",
        "bounds",
    )
    result = [diff for field in fields if bool(diff := difference(getattr(x, field), getattr(y, field)))]
    if diff := difference({i.id for i in x.metabolites}, {i.id for i in x.metabolites}):
        result.append(diff)
    return result
