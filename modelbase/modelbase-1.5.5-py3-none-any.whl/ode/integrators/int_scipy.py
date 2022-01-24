from __future__ import annotations

__all__ = [
    "_IntegratorScipy",
]

import copy
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

import numpy as np
import scipy.integrate as spi

from .abstract_integrator import AbstractIntegrator


class _IntegratorScipy(AbstractIntegrator):
    """Wrapper around scipy.odeint and scipy.ode."""

    default_integrator_kwargs = {
        "atol": 1e-8,
        "rtol": 1e-8,
    }

    def __init__(self, rhs: Callable, y0: List[float]) -> None:
        self.rhs = rhs
        self.t0 = 0.0
        self.y0 = y0
        self.y0_orig = y0.copy()
        self.kwargs: Dict[str, Any] = self.default_integrator_kwargs.copy()

    def get_integrator_kwargs(self) -> Dict[str, Any]:
        odeint_kwargs = {
            "ml": None,
            "mu": None,
            "rtol": 1e-8,  # manually set
            "atol": 1e-8,  # manually set
            "tcrit": None,
            "h0": 0.0,
            "hmax": 0.0,
            "hmin": 0.0,
            "ixpr": 0,
            "mxstep": 0,
            "mxhnil": 0,
            "mxordn": 12,
            "mxords": 5,
            "printmessg": 0,
            "tfirst": False,
        }
        ode_kwargs = {
            # internal ones
            "max_steps": 100000,
            "step_size": 1,
            # lsoda ones
            "first_step": None,
            "min_step": 0.0,
            "max_step": np.inf,
            "rtol": 1e-8,  # manually set
            "atol": 1e-8,  # manually set
            "jac": None,
            "lband": None,
            "uband": None,
        }
        return {"simulate": odeint_kwargs, "simulate_to_steady_state": ode_kwargs}

    def _simulate(
        self,
        *,
        t_end: Optional[float] = None,
        steps: Optional[int] = None,
        time_points: Optional[List[float]] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        if time_points is not None:
            if time_points[0] != 0:
                t = [self.t0]
                t.extend(time_points)
            else:
                t = time_points
            t_array = np.array(t)

        elif steps is not None and t_end is not None:
            # Scipy counts the total amount of return points rather than
            # steps as assimulo
            steps += 1
            t_array = np.linspace(self.t0, t_end, steps)
        elif t_end is not None:
            t_array = np.linspace(self.t0, t_end, 100)
        else:
            raise ValueError("You need to supply t_end (+steps) or time_points")
        y = spi.odeint(
            func=self.rhs, y0=self.y0, t=t_array, tfirst=True, **{**self.kwargs, **integrator_kwargs}
        )
        self.t0 = t_array[-1]
        self.y0 = y[-1, :]
        return list(t_array), y

    def _simulate_to_steady_state(
        self,
        *,
        tolerance: float,
        integrator_kwargs: Dict[str, Any],
        simulation_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        self.reset()
        step_size = simulation_kwargs.get("step_size", 100)
        max_steps = simulation_kwargs.get("max_steps", 1000)
        integrator = simulation_kwargs.get("integrator", "lsoda")
        integ = spi.ode(self.rhs)
        integ.set_integrator(name=integrator, **self.kwargs, **integrator_kwargs)
        integ.set_initial_value(self.y0)
        t = self.t0 + step_size
        y1 = copy.deepcopy(self.y0)
        for _ in range(max_steps):
            y2 = integ.integrate(t)
            if np.linalg.norm(y2 - y1, ord=2) < tolerance:
                return cast(List[float], t), cast(List[float], y2)
            y1 = y2
            t += step_size
        return None, None

    def reset(self) -> None:
        self.t0 = 0
        self.y0 = self.y0_orig.copy()
