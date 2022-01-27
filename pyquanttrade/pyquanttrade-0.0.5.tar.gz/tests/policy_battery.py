
from pyquanttrade.features.functions import (
    moving_average,
    upper_bollinger_band,
    lower_bollinger_band,
    get_column,
)
from pyquanttrade.policy import Policy

from pyquanttrade.features.indicators import cross_of_values


class test_policy_1(Policy):

    name = "bollinger cross"
    version = "1.0"

    # stop loss parameters:
    long_stop_loss = 100
    short_stop_loss = 100
    long_stop_loss_trailling = 100
    short_stop_loss_trailling = 100

    def description(self):
        return "Primera estrategia de prueba con reversión a la media"

    # def sell_short_when(self):
    # func1 = get_column('close')
    # func2 = lower_bollinger_band(20,20,2)
    # return cross_of_values(func2,func1)
    @classmethod
    def buy_long_when(self):
        lower_bollinger = lower_bollinger_band(50, 50, 2)
        return cross_of_values(lower_bollinger, get_column("close"))

    # def close_short_when(self):
    # func1 = get_column('close')
    # func2 = moving_average(20)
    # return cross_of_values(func1,func2)
    @classmethod
    def close_long_when(self):
        upper_bollinger = upper_bollinger_band(50, 50, 2)
        option1 = cross_of_values(get_column("close"), upper_bollinger)
        # option2 = downwards_turn(moving_average(30))
        # return apply_any([option1, option2])
        return option1

class test_policy_2(Policy):

    name = "long/short EMA crossover 10/40"
    version = "1.0"

    # stop loss parameters:
    long_stop_loss = 0.5
    short_stop_loss = 100
    long_stop_loss_trailling = 100
    short_stop_loss_trailling = 100

    def description(self):
        return "Estrategia de tipo moving average crossover. Inversión en largo cuando la SMA_10 supera SMA_40. Inversión en corto cuando la SMA_10 cae por debajo de SMA_40. Las posiciones corto/largo se cierran cuando se abren las contrarias."

    @classmethod
    def buy_long_when(self):
        func1 = moving_average(10)
        func2 = moving_average(40)
        return cross_of_values(func1, func2)

    #def sell_short_when(self):
    #    func1 = moving_average(10)
    #    func2 = moving_average(40)
    #    return cross_of_values(func2, func1)
    @classmethod
    def close_long_when(self):
        func1 = moving_average(10)
        func2 = moving_average(40)
        return cross_of_values(func2, func1)

    #def close_short_when(self):
    #    func1 = moving_average(10)
    #    func2 = moving_average(40)
    #    return cross_of_values(func1, func2)