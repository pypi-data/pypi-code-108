from __future__ import annotations

__all__ = [
    "BaseRateLaw",
    "Constant",
    "MassAction",
    "ReversibleMassAction",
    "MichaelisMenten",
    "ReversibleMichaelisMenten",
    "ReversibleMichaelisMentenKeq",
]

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, Dict, List, Union

from . import ratefunctions


def _pack_stoichiometries(substrates: List[str], products: List[str]) -> Dict[str, int]:
    new_stoichiometries: defaultdict[str, int] = defaultdict(int)
    for arg in substrates:
        new_stoichiometries[arg] -= 1
    for arg in products:
        new_stoichiometries[arg] += 1
    return dict(new_stoichiometries)


class BaseRateLaw(ABC):
    def __init__(self) -> None:
        self.substrates: List[str] = []
        self.products: List[str] = []
        self.modifiers: List[str] = []
        self.parameters: List[str] = []
        self.stoichiometry: Dict[str, int] = {}
        self.reversible: bool = False

    @abstractmethod
    def get_sbml_function_string(self) -> str:
        ...

    @abstractmethod
    def get_rate_function(self) -> Callable:
        ...


class Constant(BaseRateLaw):
    def __init__(self, product: str, k: str) -> None:
        super().__init__()
        self.products = [product]
        self.parameters = [k]
        self.stoichiometry = {product: 1}
        self.k = k

    def get_sbml_function_string(self) -> str:
        return f"{self.k}"

    def get_rate_function(self) -> Callable:
        return ratefunctions.constant


class MassAction(BaseRateLaw):
    def __init__(
        self,
        substrates: Union[str, List[str]],
        products: Union[str, List[str]],
        k_fwd: str,
    ):
        super().__init__()
        self.substrates: List[str] = list(substrates) if not isinstance(substrates, str) else [substrates]
        self.products: List[str] = list(products) if not isinstance(products, str) else [products]
        self.parameters = [k_fwd]
        self.stoichiometry = _pack_stoichiometries(self.substrates, self.products)
        self.k_fwd = k_fwd

    def get_sbml_function_string(self) -> str:
        return f"{self.k_fwd} * {' * '.join(self.substrates)}"

    def get_rate_function(self) -> Callable:
        try:
            function: Callable = getattr(ratefunctions, f"mass_action_{len(self.substrates)}")
            return function
        except AttributeError:
            return ratefunctions.mass_action_variable


class ReversibleMassAction(BaseRateLaw):
    def __init__(
        self,
        substrates: Union[str, List[str]],
        products: Union[str, List[str]],
        k_fwd: str,
        k_bwd: str,
    ):
        super().__init__()
        self.substrates: List[str] = list(substrates) if not isinstance(substrates, str) else [substrates]
        self.products: List[str] = list(products) if not isinstance(products, str) else [products]
        self.parameters = [k_fwd, k_bwd]
        self.stoichiometry = _pack_stoichiometries(self.substrates, self.products)
        self.reversible = True

        self.k_fwd = k_fwd
        self.k_bwd = k_bwd

    def get_sbml_function_string(self) -> str:
        return f"{self.k_fwd} * {' * '.join(self.substrates)} - {self.k_bwd} * {' * '.join(self.products)}"

    def get_rate_function(self) -> Callable:
        try:
            function: Callable = getattr(
                ratefunctions,
                f"reversible_mass_action_{len(self.substrates)}_{len(self.products)}",
            )
        except AttributeError:
            function = getattr(
                ratefunctions,
                f"reversible_mass_action_variable_{len(self.substrates)}",
            )
        return function


class MichaelisMenten(BaseRateLaw):
    def __init__(self, S: str, P: str, vmax: str, km: str) -> None:
        super().__init__()
        self.substrates = [S]
        self.products = [P]
        self.parameters = [vmax, km]
        self.stoichiometry = {S: -1, P: 1}

        self.S = S
        self.vmax = vmax
        self.km = km

    def get_sbml_function_string(self) -> str:
        return f"{self.S} * {self.vmax} / ({self.S} + {self.km})"

    def get_rate_function(self) -> Callable:
        return ratefunctions.michaelis_menten


class ReversibleMichaelisMenten(BaseRateLaw):
    def __init__(self, S: str, P: str, vmax_fwd: str, vmax_bwd: str, km_fwd: str, km_bwd: str) -> None:
        super().__init__()
        self.substrates = [S]
        self.products = [P]
        self.parameters = [vmax_fwd, vmax_bwd, km_fwd, km_bwd]
        self.stoichiometry = {S: -1, P: 1}
        self.reversible = True

        self.S = S
        self.P = P
        self.vmax_fwd = vmax_fwd
        self.vmax_bwd = vmax_bwd
        self.km_fwd = km_fwd
        self.km_bwd = km_bwd

    def get_sbml_function_string(self) -> str:
        return (
            f"({self.vmax_fwd} * {self.S} / {self.km_fwd} - {self.vmax_bwd} * {self.P} / {self.km_bwd})"
            + f" / (1 + {self.S} / {self.km_fwd} + {self.P} / {self.km_bwd})"
        )

    def get_rate_function(self) -> Callable:
        return ratefunctions.reversible_michaelis_menten


class ReversibleMichaelisMentenKeq(BaseRateLaw):
    def __init__(self, S: str, P: str, vmax_fwd: str, km_fwd: str, km_bwd: str, k_eq: str) -> None:
        super().__init__()
        self.substrates = [S]
        self.products = [P]
        self.parameters = [vmax_fwd, km_fwd, km_bwd, k_eq]
        self.stoichiometry = {S: -1, P: 1}
        self.reversible = True

        self.S = S
        self.P = P

        self.vmax_fwd = vmax_fwd
        self.km_fwd = km_fwd
        self.km_bwd = km_bwd
        self.k_eq = k_eq

    def get_sbml_function_string(self) -> str:
        return (
            f"{self.vmax_fwd} / {self.km_fwd} * ({self.S} - {self.P} / {self.k_eq})"
            + f"/ (1 + {self.S} / {self.km_fwd} + {self.P} / {self.km_bwd})"
        )

    def get_rate_function(self) -> Callable:
        return ratefunctions.reversible_michaelis_menten_keq
