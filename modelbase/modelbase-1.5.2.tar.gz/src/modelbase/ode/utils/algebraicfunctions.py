from __future__ import annotations

__all__ = [
    "equilibrium",
]

from typing import Tuple


def equilibrium(S: float, P: float, keq: float) -> Tuple[float, float]:
    Total = S + P
    S = Total / (1 + keq)
    P = keq * Total / (1 + keq)
    return S, P
