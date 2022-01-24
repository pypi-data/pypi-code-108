from __future__ import annotations

from functools import singledispatch
from typing import Any, Dict, List

from ..core.compound import Compound
from ..core.model import Model
from ..core.reaction import Reaction

__all__ = ["serialize"]


@singledispatch
def serialize(x: Any) -> Any:
    raise NotImplementedError(x.__class__.__name__)


@serialize.register
def _serialize_none(x: None) -> None:
    return None


@serialize.register
def _serialize_str(x: str) -> str:
    return x


@serialize.register
def _serialize_int(x: int) -> str:
    return str(x)


@serialize.register
def _serialize_float(x: float) -> str:
    return str(x)


@serialize.register
def _serialize_set(x: set) -> List[str]:
    return [serialize(i) for i in x]


@serialize.register
def _serialize_list(x: list) -> List[str]:
    return [serialize(i) for i in x]


@serialize.register
def _serialize_tuple(x: tuple) -> List[str]:
    return [serialize(i) for i in x]


@serialize.register
def _serialize_dict(x: dict) -> Dict[str, Any]:
    return {k: serialize(v) for k, v in x.items()}


@serialize.register
def _serialize_model(x: Model) -> Dict[str, Any]:
    return {
        "compounds": serialize(list(x.compounds.values())),
        "reactions": serialize(list(x.reactions.values())),
        "compartments": serialize(x.compartments),
        "objective": serialize(x.objective),
        "minimal_seed": serialize(x.minimal_seed),
        "name": serialize(x.name),
        "base_cofactor_pairs": serialize(x._base_cofactor_pairs),
    }


@serialize.register
def _serialize_compound(x: Compound) -> Dict[str, Any]:
    return {k: serialize(v) for k, v in x.__dict__.items()}


@serialize.register
def _serialize_reaction(x: Reaction) -> Dict[str, Any]:
    return {k: serialize(v) for k, v in x.__dict__.items()}
