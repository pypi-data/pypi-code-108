#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage containing user defined Island and Batch Fitness evaluator using Dask."""

import logging
import typing as t

import numpy as np
from dask import array as da
from dask import delayed as delayed

if t.TYPE_CHECKING:
    import pygmo as pg

__all__ = ["DaskBFE", "DaskIsland"]


class ProblemSerializable:
    """Create a 'problem' with a serializable fitness method.

    Method '.fitness' from a ``pg.problem`` is not serializable with 'cloudpickle'.
    Method ``ProblemSerializable.fitness`` is seriablizable with 'cloudpickle'.

    Examples
    --------
    Create a new pygmo problem and serializable problem
    >>> import pygmo as pg
    >>> prob = pg.problem(...)
    >>> prob_serial = ProblemSerializable(prob)

    Fitness function is working for the pygmo and serializable problem
    >>> import numpy as np
    >>> dvs = np.array([...])
    >>> np.array_equal(prob.fitness(dvs), prob_serial(dvs))
    True

    Serialization is not working for method 'prob.fitness' with 'cloudpickle'
    >>> import cloudpickle
    >>> _ = cloudpickle.dumps(prob.fitness)
    TypeError: cannot pickle 'PyCapsule' object

    Serialization is working with method 'prob_serial.fitness' with 'cloudpickle'
    >>> _ = cloudpickle.dumps(prob_serial.fitness)  # It's working !
    """

    def __init__(self, prob):
        self._prob = prob

    def fitness(self, *args, **kwargs):
        """Compute fitness."""
        return self._prob.fitness(*args, **kwargs)


class AlgoSerializable:
    """Create an 'algorithm' with a serializable evolve method."""

    def __init__(self, algo):
        self._algo = algo

    def evolve(self, *args, **kwargs):
        """Compute 'evolve'."""
        pop = self._algo.evolve(*args, **kwargs)

        return self._algo, pop


class DaskBFE:
    """User defined Batch Fitness Evaluator using `Dask`.

    This class is a user-defined batch fitness evaluator based on 'Dask'.
    """

    def __init__(self, chunk_size: t.Optional[int] = None):
        self._chunk_size = chunk_size

    def __call__(self, prob: "pg.problem", dvs_1d: np.ndarray) -> da.Array:
        """Call operator to run the batch fitness evaluator.

        Parameters
        ----------
        prob
        dvs_1d

        Returns
        -------
        array_like
            A 1d array with the fitness parameters.
        """
        try:
            ndims_dvs = prob.get_nx()  # type: int
            num_fitness = prob.get_nf()  # type: int

            if self._chunk_size is None:
                chunk_size = max(1, num_fitness // 10)  # type: int
            else:
                chunk_size = self._chunk_size

            # [dvs_1_1, ..., dvs_1_n, dvs_2_1, ..., dvs_2_n, ..., dvs_m_1, ..., dvs_m_n]

            # [[dvs_1_1, ..., dvs_1_n],
            #  [dvs_2_1, ..., dvs_2_n],
            #  ...
            #  [dvs_m_1, ..., dvs_m_n]]

            # Convert 1D Decision Vectors to 2D `dask.Array`
            dvs_2d = da.from_array(
                dvs_1d.reshape((-1, ndims_dvs)),
                chunks=(chunk_size, ndims_dvs),
            )  # type: da.Array

            logging.info("DaskBFE: %i, %i, %r", len(dvs_1d), ndims_dvs, dvs_2d.shape)

            # Create a new problem with a serializable method '.fitness'
            problem_pickable = ProblemSerializable(prob)

            # Create a generalized function to run a 2D input with 'prob.fitness'
            fitness_func = da.gufunc(
                problem_pickable.fitness,
                signature="(i)->(j)",
                output_dtypes=float,
                output_sizes={"j": num_fitness},
                vectorize=True,
            )

            fitness_2d = fitness_func(dvs_2d)  # type: da.Array
            fitness_1d = fitness_2d.ravel()  # type: da.Array

        except Exception:
            logging.exception("Caught an exception in 'fitness' for ModelFitting.")
            raise

        else:
            return fitness_1d

    def get_name(self) -> str:
        """Return name of this evaluator."""
        return "Dask batch fitness evaluator"

    def get_extra_info(self) -> str:
        """Return extra information for this evaluator."""
        return f"Dask batch fitness evaluator with chunk_size={self._chunk_size}."


class DaskIsland:
    """User Defined Island usind `Dask`."""

    def run_evolve(
        self, algo: "pg.algorithm", pop: "pg.population"
    ) -> t.Tuple["pg.algorithm", "pg.population"]:
        """Run 'evolve' method from the input `algorithm` to evolve the input `population`.

        Once the evolution is finished, it will return the algorithm used for the
        evolution and the evolved `population`.

        Parameters
        ----------
        algo : pg.algorithm
            Algorithm used to evolve the input population
        pop : pg.population
            Input population.

        Returns
        -------
        tuple of pg.algorithm, pg.population
            The algorithm used for the evolution and the evolved population.
        """
        logging.info("Run evolve %r, %r", pop, algo)

        # Create a new algorithm with a serializable method '.evolve'
        algo_pickable = AlgoSerializable(algo)

        # Run 'algo.evolve' with `Dask`
        new_delayed_pop = delayed(algo_pickable.evolve, nout=2)(
            pop
        )  # type: delayed.Delayed

        (
            new_algo,
            new_pop,
        ) = new_delayed_pop.compute()  # type: t.Tuple[pg.algo, pg.population]

        return new_algo, new_pop

    def get_name(self) -> str:
        """Return Island's name."""
        return "Dask Island"
