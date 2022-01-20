from typing import Callable
import numpy as np

__all__ = ["RotoSolver"]


class RotoSolver:
    def __init__(
        self,
        n_period=1.0,
        reset_to_zero=False,
        update_sequentially=True,
    ):
        r"""
        The ROTO solver is an iterative, gradient-free optimisation algorithm. It is suitable for optimisation
        variational quantum circuits with a specific structure.

        **Notes:**

        1. ROTO solver is good for a full-batch update.
        2. The ROTO solver is particularly well-suited for optimising functions
        commonly found in quantum chemistry. For the specific discussion, please
        refer to section II.A of `this paper`_.

        .. _this paper: https://arxiv.org/abs/1903.12166

        Parameters
        ----------
        n_period: float
            The number of periods the function underwent in [0,2pi). The larger the n_period, the smaller the
            periodicity of the function.
        reset_to_zero: bool
            If true, this solver will reset the $j$th parameter to $0$ prior to
            performing the parameter update rules. This strategy might not be ideal when the function to be optimised
            is stochastic.
        update_sequentially: bool
            If true, this solver will update parameter sequentially (from the first index to the last one) during each
            iteration. Otherwise, this solver will first shuffle the indices, and then update the parameter according
            to the shuffled indices.
        """
        self._use_reset_zero = reset_to_zero
        self._use_seq_udpate = update_sequentially
        self._n_period = float(n_period)

    def minimise(
        self,
        func: Callable,
        ini_variable: np.ndarray,
        extra_kwargs=None,
        max_iteration=100,
    ):  # pragma: no cover
        """
        Optimise the function `func` by updating the parameter iteratively for a maximum of `max_iteration` iterations.

        Parameters
        ----------
        func: Callable
            The function to be minimised.
        ini_variable: np.ndarray
            The initial variables from which this optimisation starts.
        extra_kwargs: dict
            Extra keyword arguments which are required by the function `func`.
        max_iteration: int
            The maximal iterations this optimisation performs.

        Returns
        -------
        np.ndarray: the modified variables after this optimisation.
        """
        variable = ini_variable
        for _ in range(max_iteration):
            variable = self.run_one_iteration(
                func=func, var=variable, extra_kwargs=extra_kwargs
            )
        return variable

    def run_one_iteration(
        self, func: Callable, var: np.ndarray, extra_kwargs=None
    ):
        """
        Performs one iteration of this solver on the function `func`, starts with the variable `var`.

        Parameters
        ----------
        func: Callable
            The function to be minimised.
        var: np.ndarray
            The initial variables from which this iteration starts.
        extra_kwargs: dict
            Extra keyword arguments which are required by the function `func`.
        Returns
        -------
        np.ndarray: the modified variables after this iteration
        """
        # How to deal with different periodicity
        # 1. transform the initial point to the new axis
        var = var * self._n_period

        # 2. to use input func to calculate values, transform the variable here back to original axis
        def func_wrapper(input_var):
            return func(input_var / self._n_period, **extra_kwargs)

        # 2. optimize in the transformed functions and variables
        theta = np.copy(var)
        iterate_idx = np.arange(len(theta))
        if not self._use_seq_udpate:
            np.random.shuffle(iterate_idx)
        if extra_kwargs is None:
            extra_kwargs = dict()

        for j in iterate_idx:
            if self._use_reset_zero:
                theta[j] = 0.0
            theta1 = np.copy(theta)
            theta1[j] -= np.pi / 2.0
            theta2 = theta
            theta3 = np.copy(theta)
            theta3[j] += np.pi / 2.0

            e1 = func_wrapper(theta1)
            e2 = func_wrapper(theta2)
            e3 = func_wrapper(theta3)

            c = (e1 + e3) / 2.0
            assert np.array_equal(theta2, theta)
            b = np.arctan2(e2 - c, e3 - c) - theta2[j]

            theta[j] = -b - np.pi / 2.0
        # 3. transform the optimised variable back to the original axis
        return theta / self._n_period
