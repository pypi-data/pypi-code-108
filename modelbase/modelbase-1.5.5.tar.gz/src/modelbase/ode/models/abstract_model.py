from __future__ import annotations

__all__ = [
    "_AbstractStoichiometricModel",
    "_AbstractRateModel",
]

from abc import ABC, abstractmethod
from typing import List, Set, Union

import numpy as np
import numpy.typing as npt

from ...core import (
    AlgebraicMixin,
    BaseModel,
    CompoundMixin,
    RateMixin,
    StoichiometricMixin,
)


class _AbstractStoichiometricModel(StoichiometricMixin, CompoundMixin, BaseModel, ABC):
    @abstractmethod
    def _get_rhs(
        self, t: Union[float, List[float], npt.NDArray[np.float64]], y: List[npt.NDArray[np.float64]]
    ) -> npt.NDArray[np.float64]:
        pass


class _AbstractRateModel(RateMixin, AlgebraicMixin, _AbstractStoichiometricModel):
    def _collect_used_parameters(self) -> Set[str]:
        used_parameters = set()
        for par in self.derived_parameters.values():
            used_parameters.update(par["parameters"])
        for module in self.algebraic_modules.values():
            used_parameters.update(module.parameters)
        for rate in self.rates.values():
            used_parameters.update(rate.parameters)
        return used_parameters

    def check_unused_parameters(self) -> Set[str]:
        used_parameters = self._collect_used_parameters()
        return set(self.parameters).difference(used_parameters)

    def check_missing_parameters(self) -> Set[str]:
        used_parameters = self._collect_used_parameters()
        return used_parameters.difference(self.parameters)

    def remove_unused_parameters(self) -> None:
        self.remove_parameters(self.check_unused_parameters())

    def _collect_used_compounds(self) -> Set[str]:
        return set((i for i in self.compounds if len(self.stoichiometries_by_compounds[i]) > 0))

    def check_unused_compounds(self) -> Set[str]:
        used_compounds = self._collect_used_compounds()
        return used_compounds.difference(self.compounds)

    def remove_unused_compounds(self) -> None:
        self.remove_compounds(self.check_unused_compounds())
