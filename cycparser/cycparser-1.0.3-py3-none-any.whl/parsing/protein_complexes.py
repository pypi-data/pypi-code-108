from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, Set

from .shared import MALFORMED_LINE_STARTS

logger = logging.getLogger(__name__)

__all__ = ["parse_complexes"]
Action = Callable[[Any, Any, Any], None]


def _add_component(complexes: Dict[str, Set[str]], complex_id: str, component: str) -> None:
    complexes[complex_id].add(component)


def parse_complexes(
    file: Iterable[str],
    actions: Dict[str, Action] | None = None,
) -> Dict[str, Set[str]]:

    if actions is None:
        actions = {
            "COMPONENTS": _add_component,
        }

    id_ = ""
    proteins: Dict[str, Set[str]] = {}
    complexes: Dict[str, Set[str]] = dict()
    for line in file:
        if any(line.startswith(i) for i in MALFORMED_LINE_STARTS):
            continue
        try:
            identifier, content = line.rstrip().split(" - ", maxsplit=1)
        except ValueError:
            logger.info(f"Malformed line in proteins.dat: {line}")
            continue

        if identifier == "UNIQUE-ID":
            id_ = content
            proteins[id_] = set()
        elif not identifier.startswith("^"):
            if (action := actions.get(identifier, None)) is not None:
                action(proteins, id_, content)

    for k, v in proteins.items():
        if bool(v):
            complexes[k] = v
    return complexes
