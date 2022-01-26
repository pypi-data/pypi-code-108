#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage containing ``typing.Protocol`` definition."""
import typing as t

import numpy as np
from typing_extensions import Protocol

if t.TYPE_CHECKING:
    import pygmo as pg

__all__ = ["IslandProtocol", "ProblemSingleObjective"]


class IslandProtocol(Protocol):
    """Protocol for a User Define Island."""

    def run_evolve(
        self, algo: "pg.algorithm", pop: "pg.population"
    ) -> t.Tuple["pg.algorithm", "pg.population"]:
        """Run 'evolve' method."""
        ...


class ProblemSingleObjective(Protocol):
    """Create a `Protocol` for a user defined Single Objective `Problem` for Pygmo2.

    A single objective is a deterministic, derivative-free, unconstrained
    optimization problem.

    See https://esa.github.io/pygmo2/problem.html#pygmo.problem.
    """

    def fitness(self, parameter: np.ndarray) -> t.Sequence[float]:
        """Return the fitness of the input decision vector.

        Concatenate the objectives, the equality and the inequality constraints.
        """
        ...

    def get_bounds(self) -> t.Tuple[t.Sequence[float], t.Sequence[float]]:
        """Get the box bounds of the problem (lower_boundary, upper_boundary).

        It also implicitly defines the dimension of the problem.
        """
        ...

    # TODO: Add something about 'batch_fitness'
    #       (see https://esa.github.io/pygmo2/problem.html#pygmo.problem.batch_fitness)
