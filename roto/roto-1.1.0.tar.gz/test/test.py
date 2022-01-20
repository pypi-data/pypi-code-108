from textwrap import shorten
import unittest

import numpy as np

from roto import RotoSolver


class _Helper:
    def __init__(self, n_param=3):
        self.kwargs_log = []
        self.arg_log = []
        self.n_param = n_param

    def __call__(self, *args, **kwargs):
        self.kwargs_log.append(kwargs)
        if len(args) != 1:
            raise ValueError(args)
        self.arg_log.append(np.copy(args[0]))
        return np.sum(args[0]).ravel()


class TestRotoSolver(unittest.TestCase):
    def test_the_function_has_been_correctly_called_in_normal_setup(self):
        func = _Helper(n_param=3)
        roto = RotoSolver(reset_to_zero=False, update_sequentially=True)
        var = np.arange(3).astype(float)
        kwargs = {'a': 1, 'b': 2}

        roto.run_one_iteration(func=func, var=var, extra_kwargs=kwargs)
        self.assertTrue(all(k == kwargs for k in func.kwargs_log))

        should_be = np.array(
            [
                [-1.57079633, 1., 2.], [0., 1., 2.], [1.57079633, 1., 2.],
                [-1.57079633, -0.57079633, 2.], [-1.57079633, 1., 2.],
                [-1.57079633, 2.57079633, 2.],
                [-1.57079633, -0.57079633, 0.42920367],
                [-1.57079633, -0.57079633, 2.],
                [-1.57079633, -0.57079633, 3.57079633]
            ]
        )
        print('np.asarray(should_be):\n', repr(np.asarray(func.arg_log)))
        self.assertTrue(
            all(
                np.allclose(should_be[i], item)
                for i, item in enumerate(func.arg_log)
            )
        )

    def test_the_function_has_been_correctly_called_with_modified_param(self):
        func = _Helper(n_param=3)
        np.random.seed(
            1
        )  # seed it such that when not update_sequentially, the behaviour is predictable.
        roto = RotoSolver(reset_to_zero=True, update_sequentially=False)
        var = np.arange(3).astype(float)
        kwargs = {'a': 1, 'b': 2}

        roto.run_one_iteration(func=func, var=var, extra_kwargs=kwargs)
        self.assertTrue(all(k == kwargs for k in func.kwargs_log))

        should_be = np.array(
            [
                [-1.57079633, 1., 2.], [0., 1., 2.], [1.57079633, 1., 2.],
                [-1.57079633, 1., -1.57079633], [-1.57079633, 1., 0.],
                [-1.57079633, 1., 1.57079633],
                [-1.57079633, -1.57079633, -1.57079633],
                [-1.57079633, 0., -1.57079633],
                [-1.57079633, 1.57079633, -1.57079633]
            ]
        )
        self.assertTrue(
            all(
                np.allclose(should_be[i], item)
                for i, item in enumerate(func.arg_log)
            )
        )

    def test_suc_minimised(self):
        np.random.seed(10)
        size = 20
        a, b, c, k = [np.random.rand(size) for _ in range(4)]

        # Note: although the reason being unclear, the fact that RotoSolver can succesfully
        # minimise this function below might be due to k is unifomly distributed in [0, 1)
        def func(var):
            return np.sum(a * np.sin(k * var + b) + c)

        x0 = np.random.rand(20)

        # print('\nrestart with x optimum\n')
        var = RotoSolver().minimise(func, x0, max_iteration=100)
        should_be = np.array(
            [
                -3.53773183, -1.89732622, -3.63690614, -3.80366784,
                -51.23571681, -5.61285752, -27.48999318, -6.82228484,
                -6.71624979, -2.8066041, -59.46112552, -4.87190125, -7.87308239,
                -2.96945596, -4.79650454, -43.42485359, -1.91470807,
                -3.14380248, -1.84227176, -5.26236014
            ]
        )
        self.assertTrue(np.allclose(var, should_be))
        self.assertTrue(np.allclose(func(var), 0.1675518937516567))

    def test_suc_minimised_diff_period(self):
        rng = np.random.default_rng(seed=540)
        size = rng.integers(low=5, high=10)
        a, b = [rng.uniform(low=-5, high=5, size=size) for _ in range(2)]
        should_be = -np.product(np.abs(a))  # theoretical minimum

        k = 2.0

        def func(var):
            return np.product(a * np.sin(k * var + b))

        x0 = rng.uniform(low=0, high=2 * np.pi, size=size)

        result = RotoSolver(n_period=k).minimise(func, x0, max_iteration=100)

        assert not np.allclose(func(x0), func(result), atol=0.1)
        assert np.allclose(func(result), should_be, atol=1e-8)


if __name__ == '__main__':
    TestRotoSolver(
    ).test_the_function_has_been_correctly_called_in_normal_setup()
