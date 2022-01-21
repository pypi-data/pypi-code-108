from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable

from ..data import Enzyme
from .shared import MALFORMED_LINE_STARTS

__all__ = ["parse_enzymes"]

logger = logging.getLogger(__name__)
Action = Callable[[Any, Any, Any], None]
SubAction = Dict[str, Callable[[Any, Any, Any, Any], None]]


def _set_cplx_or_monomer(enzrxns: Dict[str, Enzyme], id_: str, cplx_or_monomer: str) -> None:
    enzrxns[id_].cplx_or_monomer = cplx_or_monomer


def _add_kcat(enzrxns: Dict[str, Enzyme], id_: str, substrate: str, kcat: str) -> None:
    try:
        enzrxns[id_].kinetic_data.kcat.setdefault(substrate, float(kcat))
    except ValueError:  # conversion failed
        pass


def _add_km(enzrxns: Dict[str, Enzyme], id_: str, substrate: str, km: str) -> None:
    try:
        enzrxns[id_].kinetic_data.km.setdefault(substrate, float(km))
    except ValueError:  # conversion failed
        pass


def _add_vmax(enzrxns: Dict[str, Enzyme], id_: str, substrate: str, vmax: str) -> None:
    try:
        enzrxns[id_].kinetic_data.vmax.setdefault(substrate, float(vmax))
    except ValueError:  # conversion failed
        pass


def parse_enzymes(
    file: Iterable[str],
    actions: Dict[str, Action] | None = None,
    sub_actions: Dict[str, SubAction] | None = None,
) -> Dict[str, Enzyme]:

    if actions is None:
        actions = {
            "ENZYME": _set_cplx_or_monomer,
        }
    if sub_actions is None:
        sub_actions = {
            "^SUBSTRATE": {"KM": _add_km, "VMAX": _add_vmax, "KCAT": _add_kcat},
        }

    id_ = ""
    enzrxns = {}
    last_identifier = ""
    last_content = ""
    for line in file:
        if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
            continue
        try:
            identifier, content = line.rstrip().split(" - ", maxsplit=1)
        except ValueError:
            logger.info(f"Malformed line in enzymes.dat {line}")
            continue

        if identifier == "UNIQUE-ID":
            id_ = content
            enzrxns[id_] = Enzyme(id=id_)
        elif identifier.startswith("^"):
            if (subaction := sub_actions.get(identifier, {}).get(last_identifier, None)) is not None:
                subaction(enzrxns, id_, content, last_content)
        else:
            if (action := actions.get(identifier, None)) is not None:
                action(enzrxns, id_, content)
                last_identifier = identifier
                last_content = content
    return enzrxns
