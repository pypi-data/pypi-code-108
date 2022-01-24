from __future__ import annotations

__all__ = [
    "AbstractIntegrator",
]

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt


class AbstractIntegrator(ABC):
    """Interface for integrators"""

    def __init__(self, rhs: Callable, y0: Union[npt.NDArray[np.float64], List[float]]) -> None:
        self.kwargs: Dict[str, Any] = {}
        self.rhs = rhs
        self.y0 = y0

    @abstractmethod
    def reset(self) -> None:
        """Reset the integrator and simulator state"""
        ...

    @abstractmethod
    def _simulate(
        self,
        *,
        t_end: Optional[float] = None,
        steps: Optional[int] = None,
        time_points: Optional[List[float]] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        ...

    @abstractmethod
    def _simulate_to_steady_state(
        self,
        *,
        tolerance: float,
        integrator_kwargs: Dict[str, Any],
        simulation_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        ...

    @abstractmethod
    def get_integrator_kwargs(self) -> Dict[str, Any]:
        """Get possible integration settings"""
        ...
