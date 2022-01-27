#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
"""TBW."""

import math
import typing as t
from enum import Enum

from typing_extensions import Literal

try:
    import pygmo as pg
except ImportError:
    pass

__all__ = ["Algorithm", "AlgorithmType"]


class AlgorithmType(Enum):
    """TBW."""

    Sade = "sade"
    Sga = "sga"
    Nlopt = "nlopt"


# TODO: Use a class `Sade`, `SGA` and `NLOPT`. See #334
class Algorithm:
    """TBW."""

    def __init__(
        self,
        # TODO: Rename 'type' into 'algorithm_type'. See #334
        type: Literal["sade", "sga", "nlopt"] = "sade",
        generations: int = 1,
        population_size: int = 1,
        # SADE #####
        variant: int = 2,
        variant_adptv: int = 1,
        ftol: float = 1e-6,
        xtol: float = 1e-6,
        memory: bool = False,
        # SGA #####
        cr: float = 0.9,
        eta_c: float = 1.0,
        m: float = 0.02,
        param_m: float = 1.0,
        param_s: int = 2,
        crossover: str = "exponential",
        mutation: str = "polynomial",
        selection: str = "tournament",
        # NLOPT #####
        nlopt_solver: str = "neldermead",
        maxtime: int = 0,
        maxeval: int = 0,
        xtol_rel: float = 1.0e-8,
        xtol_abs: float = 0.0,
        ftol_rel: float = 0.0,
        ftol_abs: float = 0.0,
        stopval: float = -math.inf,
        local_optimizer: t.Optional["pg.nlopt"] = None,
        replacement: str = "best",
        nlopt_selection: str = "best",
    ):
        if generations not in range(1, 100001):
            raise ValueError("'generations' must be between 1 and 100000.")

        if population_size not in range(1, 100001):
            raise ValueError("'population_size' must be between 1 and 100000.")

        self._type = AlgorithmType(type)
        self._generations = generations
        self._population_size = population_size

        # SADE #####
        if variant not in range(1, 19):
            raise ValueError("'variant' must be between 1 and 18.")

        if variant_adptv not in (1, 2):
            raise ValueError("'variant_adptv' must be between 1 and 2.")

        self._variant = variant
        self._variant_adptv = variant_adptv
        self._ftol = ftol
        self._xtol = xtol
        self._memory = memory

        # SGA #####
        if not (0.0 <= cr <= 1.0):
            raise ValueError("'cr' must be between 0.0 and 1.0.")

        if not (0.0 <= m <= 1.0):
            raise ValueError("'m' must be between 0.0 and 1.0.")

        self._cr = cr
        self._eta_c = eta_c
        self._m = m
        self._param_m = param_m
        self._param_s = param_s
        self._crossover = crossover
        self._mutation = mutation
        self._selection = selection

        # NLOPT #####
        self._nlopt_solver = nlopt_solver
        self._maxtime = maxtime
        self._maxeval = maxeval
        self._xtol_rel = xtol_rel
        self._xtol_abs = xtol_abs
        self._ftol_rel = ftol_rel
        self._ftol_abs = ftol_abs
        self._stopval = stopval
        self._local_optimizer = local_optimizer  # type: t.Optional[pg.nlopt]
        self._replacement = replacement
        self._nlopt_selection = nlopt_selection

    @property
    def type(self) -> AlgorithmType:
        """TBW."""
        return self._type

    @type.setter
    def type(self, value: AlgorithmType) -> None:
        """TBW."""
        self._type = AlgorithmType(value)

    @property
    def generations(self) -> int:
        """TBW."""
        return self._generations

    @generations.setter
    def generations(self, value: int) -> None:
        """TBW."""
        if value not in range(1, 100001):
            raise ValueError("'generations' must be between 1 and 100000.")

        self._generations = value

    @property
    def population_size(self) -> int:
        """TBW."""
        return self._population_size

    @population_size.setter
    def population_size(self, value: int) -> None:
        """TBW."""
        if value not in range(1, 100001):
            raise ValueError("'population_size' must be between 1 and 100000.")

        self._population_size = value

    # SADE #####
    @property
    def variant(self) -> int:
        """TBW."""
        return self._variant

    @variant.setter
    def variant(self, value: int) -> None:
        """TBW."""
        if value not in range(1, 19):
            raise ValueError("'variant' must be between 1 and 18.")

        self._variant = value

    @property
    def variant_adptv(self) -> int:
        """TBW."""
        return self._variant_adptv

    @variant_adptv.setter
    def variant_adptv(self, value: int) -> None:
        """TBW."""
        if value not in (1, 2):
            raise ValueError("'variant_adptv' must be between 1 and 2.")

        self._variant_adptv = value

    @property
    def ftol(self) -> float:
        """TBW."""
        return self._ftol

    @ftol.setter
    def ftol(self, value: float) -> None:
        """TBW."""
        self._ftol = value

    @property
    def xtol(self) -> float:
        """TBW."""
        return self._xtol

    @xtol.setter
    def xtol(self, value: float) -> None:
        """TBW."""
        self._xtol = value

    @property
    def memory(self) -> bool:
        """TBW."""
        return self._memory

    @memory.setter
    def memory(self, value: bool) -> None:
        """TBW."""
        self._memory = value

    # SADE #####

    # SGA #####
    @property
    def cr(self) -> float:
        """TBW."""
        return self._cr

    @cr.setter
    def cr(self, value: float) -> None:
        """TBW."""
        if not (0.0 <= value <= 1.0):
            raise ValueError("'cr' must be between 0.0 and 1.0.")

        self._cr = value

    @property
    def eta_c(self) -> float:
        """TBW."""
        return self._eta_c

    @eta_c.setter
    def eta_c(self, value: float) -> None:
        """TBW."""
        self._eta_c = value

    @property
    def m(self) -> float:
        """TBW."""
        return self._m

    @m.setter
    def m(self, value: float) -> None:
        """TBW."""
        if not (0.0 <= value <= 1.0):
            raise ValueError("'m' must be between 0.0 and 1.0.")

        self._m = value

    @property
    def param_m(self) -> float:
        """TBW."""
        return self._param_m

    @param_m.setter
    def param_m(self, value: float) -> None:
        """TBW."""
        self._param_m = value

    @property
    def param_s(self) -> int:
        """TBW."""
        return self._param_s

    @param_s.setter
    def param_s(self, value: int) -> None:
        """TBW."""
        self._param_s = value

    @property
    def crossover(self) -> str:
        """TBW."""
        return self._crossover

    @crossover.setter
    def crossover(self, value: str) -> None:
        """TBW."""
        self._crossover = value

    @property
    def mutation(self) -> str:
        """TBW."""
        return self._mutation

    @mutation.setter
    def mutation(self, value: str) -> None:
        """TBW."""
        self._mutation = value

    @property
    def selection(self) -> str:
        """TBW."""
        return self._selection

    @selection.setter
    def selection(self, value: str) -> None:
        """TBW."""
        self._selection = value

    # SGA #####

    # NLOPT #####
    @property
    def nlopt_solver(self) -> str:
        """TBW."""
        return self._nlopt_solver

    @nlopt_solver.setter
    def nlopt_solver(self, value: str) -> None:
        """TBW."""
        self._nlopt_solver = value

    @property
    def maxtime(self) -> int:
        """TBW."""
        return self._maxtime

    @maxtime.setter
    def maxtime(self, value: int) -> None:
        """TBW."""
        self._maxtime = value

    @property
    def maxeval(self) -> int:
        """TBW."""
        return self._maxeval

    @maxeval.setter
    def maxeval(self, value: int) -> None:
        """TBW."""
        self._maxeval = value

    @property
    def xtol_rel(self) -> float:
        """TBW."""
        return self._xtol_rel

    @xtol_rel.setter
    def xtol_rel(self, value: float) -> None:
        """TBW."""
        self._xtol_rel = value

    @property
    def xtol_abs(self) -> float:
        """TBW."""
        return self._xtol_abs

    @xtol_abs.setter
    def xtol_abs(self, value: float) -> None:
        """TBW."""
        self._xtol_abs = value

    @property
    def ftol_rel(self) -> float:
        """TBW."""
        return self._ftol_rel

    @ftol_rel.setter
    def ftol_rel(self, value: float) -> None:
        """TBW."""
        self._ftol_rel = value

    @property
    def ftol_abs(self) -> float:
        """TBW."""
        return self._ftol_abs

    @ftol_abs.setter
    def ftol_abs(self, value: float) -> None:
        """TBW."""
        self._ftol_abs = value

    @property
    def stopval(self) -> float:
        """TBW."""
        return self._stopval

    @stopval.setter
    def stopval(self, value: float) -> None:
        """TBW."""
        self._stopval = value

    @property
    def local_optimizer(self) -> t.Optional["pg.nlopt"]:
        """TBW."""
        return self._local_optimizer

    @local_optimizer.setter
    def local_optimizer(self, value: t.Optional["pg.nlopt"]) -> None:
        """TBW."""
        self._local_optimizer = value

    @property
    def replacement(self) -> str:
        """TBW."""
        return self._replacement

    @replacement.setter
    def replacement(self, value: str) -> None:
        """TBW."""
        self._replacement = value

    @property
    def nlopt_selection(self) -> str:
        """TBW."""
        return self._nlopt_selection

    @nlopt_selection.setter
    def nlopt_selection(self, value: str) -> None:
        """TBW."""
        self._nlopt_selection = value

    # NLOPT #####

    # TODO: This could be refactored for each if-statement. See #334
    def get_algorithm(self) -> t.Union["pg.sade", "pg.sga", "pg.nlopt"]:
        """TBW.

        :return:
        """
        if self.type is AlgorithmType.Sade:
            sade_algorithm = pg.sade(
                gen=self.generations,
                variant=self.variant,
                variant_adptv=self.variant_adptv,
                ftol=self.ftol,
                xtol=self.xtol,
                memory=self.memory,
            )  # type: pg.sade

            return sade_algorithm

        elif self.type is AlgorithmType.Sga:
            # mutation parameter
            sga_algorithm = pg.sga(
                gen=self.generations,
                cr=self.cr,  # crossover probability
                crossover=self.crossover,  # single, exponential, binomial, sbx
                m=self.m,  # mutation probability
                mutation=self.mutation,  # uniform, gaussian, polynomial
                param_s=self.param_s,  # number of best ind. in 'truncated'/tournament
                selection=self.selection,  # tournament, truncated
                eta_c=self.eta_c,  # distribution index for sbx crossover
                param_m=self.param_m,
            )  # type: pg.sga

            return sga_algorithm

        elif self.type is AlgorithmType.Nlopt:
            opt_algorithm = pg.nlopt(self.nlopt_solver)  # type: pg.nlopt
            opt_algorithm.maxtime = (
                self.maxtime
            )  # stop when the optimization time (in seconds) exceeds maxtime
            opt_algorithm.maxeval = (
                self.maxeval
            )  # stop when the number of function evaluations exceeds maxeval
            opt_algorithm.xtol_rel = self.xtol_rel  # relative stopping criterion for x
            opt_algorithm.xtol_abs = self.xtol_abs  # absolute stopping criterion for x
            opt_algorithm.ftol_rel = self.ftol_rel
            opt_algorithm.ftol_abs = self.ftol_abs
            opt_algorithm.stopval = self.stopval
            opt_algorithm.local_optimizer = self.local_optimizer
            opt_algorithm.replacement = self.replacement
            opt_algorithm.selection = self.nlopt_selection

            return opt_algorithm

        else:
            raise NotImplementedError
