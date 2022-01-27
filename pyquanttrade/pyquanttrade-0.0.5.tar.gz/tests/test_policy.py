"""
from trading.policy_analysis.searching_algos import grid_search, manhattan_distance
from trading.policy_analysis.walkforward import sequential_backtesting

from trading.policies_backtesting import policies


class std_policy(Policy):
    name = "test_policy"

    @classmethod
    def set_attribs(cls, param1, param2):
        cls.param1 = param1
        cls.param2 = param2
        cls.buffer = max(param1, param2)
        return cls

    long_stop_loss = 100
    short_stop_loss = 100
    long_stop_loss_trailling = 100
    short_stop_loss_trailling = 100

    @classmethod
    def buy_long_when(cls):
        return cross_of_values(moving_average(cls.param1), moving_average(cls.param2))

    @classmethod
    def close_long_when(cls):
        return cross_of_values(moving_average(cls.param2), moving_average(cls.param1))


def test_optimiser():
    param_set = {"param1": [5, 10], "param2": [20, 30]}
    grid_search(
        std_policy, param_set, ["2010-01-01", "2011-12-31"], "INTC", 1, [15, 20]
    )


def test_manhattan_distance():
    param_set_1 = [0, 2, 3]
    param_set_2 = [1, 3, 5]
    steps = [1, 0.5, 2]
    assert manhattan_distance(param_set_1, param_set_2, steps) == 4


def test_sequential_backtesting():
    param_set = {"param1": [5, 10], "param2": [20, 30]}
    (
        overall_backtest_results,
        rolling_backtest_results,
        iter_params,
    ) = sequential_backtesting(
        std_policy,
        'grid_search',
        param_set,
        ["2010-01-01", "2018-12-31"],
        "INTC",
        600,
        300,
        1,
        [15, 20],
    )
    assert iter_params

"""