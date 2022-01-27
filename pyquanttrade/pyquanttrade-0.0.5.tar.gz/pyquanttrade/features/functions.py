# -*- coding: utf-8 -*-
"""
Functions to create strategies.

All of the functions return a *programatic function* which calculates the given function for some OCHL data.

To build a function not included in the package, use the following template::

    def function_name(params, target='close'):
        def return_function(data):
            your code goes here
        return return_function

"""

import numpy as np


def days_to_constant(days, order=1):
    #TODO: Finish documenting
    """
    .. _days_to_constant:

    Calculates the constant for exponential smoothing from a given window size

    :param days: Window size
    :type days: int
    :param order: [description], defaults to 1
    :type order: int, optional
    """
    return float("%.3f" % (1 - pow(1 - 2 / (days + 1), 1 / order)))


def get_column(column):
    def return_function(data):
        return data[column].copy()

    return return_function

def trailing(target="close", days=40, over_under="under"):
    """
    Calculates the if the target is trailing under or over the current in the past days.

    :param target: Data column to use for the calculation, defaults to "close"
    :type target: str
    :param days: Size of the window in days, defaults to 40
    :type days: int
    """
    def f():
        def g(x):
            return all(x[-1] > x[:-1])

        return g

    def return_function(data):
        column_name = f"trailling_{over_under}_{days}_of_{target}"
        if column_name not in data.columns:
            data[column_name] = (
                data[target].rolling(window=days, min_periods=1).apply(f(), raw=True)
            )
        return data[column_name].copy()

    return return_function


def rolling_std(days, target="close"):
    """Calculates the rolling standard deviation

    :param days: Size of the window in days
    :type days: int
    :param target: Data column to use for the calculation, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"rolling_std_{days}_of_{target}"
        if column_name not in data.columns:
            data[column_name] = data[target].rolling(days, min_periods=2).std()
        return data[column_name].copy()

    return return_function


def moving_average(days, target="close"):
    """Calculates the rolling moving average

    :param days: Size of the window in days
    :type days: int
    :param target: Data column to use for the calculation, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"moving_average_{days}_of_{target}"
        if column_name not in data.columns:
            data[column_name] = data[target].rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def weighted_moving_average(days, weights):
    """Calculates the rolling weighted moving average. The weights list should have the size of the days window.

    :param days: Size of the window
    :type days: int
    :param weights: Weights to use for the calculation
    :type weights: list(int)
    """
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        if len(weights) == days:
            column_name = f"weighted_moving_average_{days}"
            if column_name not in data.columns:
                data[column_name] = (
                    data["close"].rolling(window=days).apply(f(weights), raw=True)
                )
            return data[column_name].copy()
        else:
            raise Exception("Weights length and rolling mean must be same length")

    return return_function


def step_weighting_ma(days, first_weight=1, step=1):
    """Calculates the weighted moving average using stepped weights

    :param days: Window size
    :type days: int
    :param first_weight: Weight of the first data point, defaults to 1
    :type first_weight: int, optional
    :param step: Weight increment for each data point, defaults to 1
    :type step: int, optional
    """
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        weights = np.linspace(first_weight, (days * step) + first_weight - step, days)
        column_name = f"step_weighting_ma_{days}"
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def percentage_weighting_ma(days, last_weight=1, step=0.5):
    """Calculates the weighted moving average using backwards set weights. F.e. for a given last days=3, weight=1, step=0.5, the wieghts would be [0.25, 0.5, 1]

    :param days: Window size
    :type days: int
    :param last_weight: Weights of the last data point, defaults to 1
    :type last_weight: int, optional
    :param step: Weight multiplier for each previous data point, defaults to 0.5
    :type step: float, optional
    """
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        weights = np.zeros(days)
        weights[-1] = last_weight
        for i in range(1, days):
            weights[-1 * (i + 1)] = weights[-1 * i] * step
        column_name = f"percentage_weighting_ma_{days}"
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def triangular_weighting_ma(days=10, shape="linear"):
    """Calculates the weighted moving average with the weights having a triangular shape

    :param days: Window size, defaults to 10
    :type days: int, optional
    :param shape: Type of shape. Can be "linear" or "gaussian" , defaults to "linear"
    :type shape: str, optional
    """
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def linear_triangular_weights():
        weights = np.zeros(days)
        weights[0 : int((days + 2) / 2) - 1] = range(1, int((days + 2) / 2))
        if days % 2 == 0:
            weights[int((days + 2) / 2) - 1 :] = range(1, int((days + 2) / 2))[::-1]
        else:
            weights[int((days + 2) / 2) - 1 :] = range(1, int((days + 2) / 2) + 1)[::-1]
        return weights

    def gaussian_triangular_weights():
        return NotImplementedError()

    if shape not in ["linear", "gaussian"]:
        raise NotImplementedError()
    else:
        weight_options = {
            "linear": linear_triangular_weights,
            "gaussian": gaussian_triangular_weights,
        }
        weights_func = weight_options.get(shape)
        weights_values = weights_func()

    def return_function(data):
        column_name = f"{shape}_trianguar_weighting_ma_{days}"
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights_values), raw=True)
            )
        return data[column_name].copy()

    return return_function


def pivot_point_weighting_ma(days):
    #TODO: Review the implementation of this function. Pivot point in the internet is referred by the internet to the moving average
    #of (close+high+low)/3. Refer to the book.
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def pivot_point_weights():
        weights = np.array(range(1, days + 1))
        weights = weights * 3 - days - 1
        return weights

    def return_function(data):
        weights = pivot_point_weights()
        column_name = f"pivot_point_weighting_ma_{days}"
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def geometric_moving_average(days, target='close'):
    """Calculates the geometric moving average

    :param days: Window size
    :type days: int
    :param target: Data column to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"geometric_moving_average_{days}"
        if column_name not in data.columns:
            data[column_name] = pow(
                data[target].rolling(window=days).apply(np.prod, raw=True), 1 / days
            )
        return data[column_name].copy()

    return return_function


def exponential_smoothing(constant, target="close"):
    """Calculates the exponential smoothing

    :param constant: Smoothing constant for the calculation. Use function days_to_constant_
    :type constant: float
    :param target: Data column to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"exponential_smoothing_{constant}%_of_{target}"
        if column_name not in data.columns:
            data[column_name] = data[target].copy()
            for i in data[data[target].notnull()].index[1:]:
                data.loc[i, column_name] = data[column_name].loc[:i][-2] + constant * (
                    data[target].loc[i] - data[column_name].loc[:i][-2])

        return data[column_name].copy()

    return return_function


def second_order_exponential_smoothing(constant):
    """Calculates the second order exponential smoothing of close

    :param constant: Smoothing constant for the calculation. Use function days_to_constant_
    :type constant: float
    """
    def return_function(data):
        first_order = exponential_smoothing(constant)(data)
        column_name = f"second_order_exponential_smoothing_{constant}%"
        if column_name not in data.columns:
            data[column_name] = first_order.copy()
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    first_order.iloc[i] - data[column_name].iloc[i - 1]
                )
        return data[column_name].copy()

    return return_function


def third_order_exponential_smoothing(constant):
    """Calculates the second order exponential smoothing of close

    :param constant: Smoothing constant for the calculation. Use function days_to_constant_
    :type constant: float
    """
    def return_function(data):
        second_order = second_order_exponential_smoothing(constant)(data)
        column_name = f"third_order_exponential_smoothing_{constant}%"
        if column_name not in data.columns:
            data[column_name] = second_order.copy()
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    second_order.iloc[i] - data[column_name].iloc[i - 1]
                )
        return data[column_name].copy()

    return return_function


def lag_correction_exponential_smoothing(constant):
    #TODO: View the book for explanation
    def return_function(data):
        column_name = (f"lag_correction_exponential_smoothing_{constant*100}%")
        if column_name not in data.columns:
            first_order = exponential_smoothing(constant)(data)
            data[column_name] = data["close"] - first_order
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    data[column_name].iloc[i] - data[column_name].iloc[i - 1]
                )
            data[column_name] = data[column_name] + first_order
        return data[column_name].copy()

    return return_function


def double_moving_average(days):
    """Calculates the double moving average of close

    :param days: Window size
    :type days: int
    """
    def return_function(data):
        column_name = f"double_moving_average_{days}"
        if column_name not in data.columns:
            simple_ma = moving_average(days)(data)
            data[column_name] = simple_ma.rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def double_smoothed_momentum(days1, days2):
    """Calculates the momentum, smoothed by two consecutive exponential smoothings
    
    :param days1: First smoothing window size
    :type days1: int
    :param days2: Second smoothing window size
    :type days2: int
    """
    def return_function(data):
        column_name = f"DSM{days1}/{days2}"
        if column_name not in data.columns:
            momentum_val = momentum(days=days1)(data)
            constant = days_to_constant(days1)
            exp_smoothed = exponential_smoothing(constant, target=momentum_val.name)(
                data
            )
            constant = days_to_constant(days2, 2)
            data[column_name] = exponential_smoothing(
                constant, target=exp_smoothed.name
            )(data)
        return data[column_name].copy()

    return return_function


def regularized_exponential_ma(days, weight, target="close"):
    #TODO: Refer to book
    def return_function(data):
        column_name = f"REMA_{days}/{weight}_of_{target}"
        if column_name not in data.columns:
            c = days_to_constant(days)
            data[column_name] = data[target].copy()
            for i in range(2, len(data)):
                data[column_name].iloc[i] = (
                    data[column_name].iloc[i - 1] * (1 + 2 * weight)
                    + c * (data[column_name].iloc[i] - data[column_name].iloc[i - 1])
                    - weight * data[column_name].iloc[i - 2]
                ) / (1 + weight)
        return data[column_name].copy()

    return return_function


def hull_moving_average(period=16, target="close"):
    """Calculates the hull moving average

    :param period: Window size, defaults to 16
    :type period: int, optional
    :param target: Data colum to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"hull_moving_average_{period}_of_{target}"
        if column_name not in data.columns:
            period_ma = moving_average(period)(data)
            period2_ma = moving_average(int(period / 2))(data)
            data[column_name] = (
                (2 * period2_ma - period_ma)
                .rolling(int(pow(period, 1 / 2)), min_periods=1)
                .mean()
            )
        return data[column_name].copy()

    return return_function


def upper_keltner_channel(days=10):
    """Calculates the upper keltner channel

    :param days: Window size, defaults to 10
    :type days: int, optional
    """
    def return_function(data):
        column_name = f"upper_keltner_{days}"
        if column_name not in data.columns:
            average_daily_price = (data["close"] + data["high"] + data["low"]) / 3
            if (f"moving_average_{days}_of_close") not in data.columns:
                moving_average(days)(data)
            data[column_name] = (
                data[f"moving_average_{days}_of_close"] + average_daily_price
            )
        return data[column_name].copy()

    return return_function


def lower_keltner_channel(days=10):
    """Calculates the lower keltner channel

    :param days: Window size, defaults to 10
    :type days: int, optional
    """
    def return_function(data):
        column_name = f"lower_keltner_{days}"
        if column_name not in data.columns:
            average_daily_price = (data["close"] + data["high"] + data["low"]) / 3
            if (f"moving_average_{days}_of_close") not in data.columns:
                moving_average(days)(data)
            data[column_name] = (
                data[f"moving_average_{days}_of_close"] - average_daily_price
            )
        return data[column_name].copy()

    return return_function


def upper_percentage_band(c, band_target, center_target):
    """Calculates the upper percentage band

    :param c: multiplier constant
    :type c: float
    :param band_target: Data column used for the band displacement
    :type band_target: str
    :param center_target: Data column used for the center of the channel
    :type center_target: str
    """
    def return_function(data):
        column_name = f"upper_percentage_band_{c}_of_{band_target.name}_over_{center_target.name}"
        if column_name not in data.columns:
            print(center_target)
            data[column_name] = c * band_target + center_target.values
        return data[column_name].copy()

    return return_function


def lower_percentage_band(c, band_target, center_target):
    """Calculates the lower percentage band

    :param c: multiplier constant
    :type c: float
    :param band_target: Data column used for the band displacement
    :type band_target: str
    :param center_target: Data column used for the center of the channel
    :type center_target: str
    """
    def return_function(data):
        column_name = f"lower_percentage_band_{c}_of_{band_target.name}_under_{center_target.name}"
        if column_name not in data.columns:
            data[column_name] = -c * band_target + center_target.values
        return data[column_name].copy()

    return return_function


def upper_absolute_band(value, target):
    """Calculates the upper absolute band

    :param value: Constant for band displacement
    :type value: float
    :param target: Data column for the center of the band
    :type target: str
    """
    def return_function(data):
        column_name = f"upper_absolute_band_{value}_over_{target.name}"
        if column_name not in data.columns:
            data[column_name] = value + target
        return data[column_name].copy()

    return return_function


def lower_absolute_band(value, target):
    """Calculates the lower absolute band

    :param value: Constant for band displacement
    :type value: float
    :param target: Data column for the center of the band
    :type target: str
    """
    def return_function(data):
        column_name = f"lower_absolute_band_{value}_under_{target.name}"
        if column_name not in data.columns:
            data[column_name] = -value + target
        return data[column_name].copy()

    return return_function


def upper_bollinger_band(mean_days, std_days, c):
    """Calculates the upper bollinger band

    :param mean_days: Window size for the band center
    :type mean_days: int
    :param std_days: Window size for the band displacement
    :type std_days: str
    :param c: Multiplier constant
    :type c: float
    """
    def return_function(data):
        column_name = f"upper_bollinger_band_{mean_days}/{std_days}"
        if column_name not in data.columns:
            std_dev = rolling_std(std_days)(data)
            ma = moving_average(mean_days)(data)
            data[column_name] = ma + c * std_dev
        return data[column_name].copy()

    return return_function


def lower_bollinger_band(mean_days, std_days, c):
    """Calculates the lower bollinger band

    :param mean_days: Window size for the band center
    :type mean_days: int
    :param std_days: Window size for the band displacement
    :type std_days: str
    :param c: Multiplier constant
    :type c: float
    """
    def return_function(data):
        column_name = f"lower_bollinger_band_{mean_days}/{std_days}"
        if column_name not in data.columns:
            std_dev = rolling_std(std_days)(data)
            ma = moving_average(mean_days)(data)
            data[column_name] = ma - c * std_dev
        return data[column_name].copy()

    return return_function


def upper_volatility_band(c, dev_target, band_target, center_target):
    """Calculates the upper volatility band

    :param c: Multiplier constant
    :type c: float
    :param dev_target: Used for band displacement. Can be a constant or a function
    :type dev_target: function or float
    :param band_target: Used for band displacement. Can be a constant or a function
    :type band_target: function or float
    :param center_target: Data column for the band center
    :type center_target: str
    """
    def return_function(data):
        if hasattr(band_target, "name") & hasattr(dev_target, "name"):
            column_name = f"upper_volatility_band_{c}_times_{band_target.name}&{dev_target.name}_over_{center_target.name}"
        elif hasattr(band_target, "name"):
            column_name = f"upper_volatility_band_{c}_times_{band_target.name}&{dev_target}_over_{center_target.name}"
        else:
            column_name = f"upper_volatility_band_{c}_times_{band_target}&{dev_target}_over_{center_target.name}"
        if column_name not in data.columns:
            data[column_name] = center_target + c * dev_target * band_target
        return data[column_name].copy()

    return return_function


def lower_volatility_band(c, dev_target, band_target, center_target):
    """Calculates the lower volatility band

    :param c: Multiplier constant
    :type c: float
    :param dev_target: Used for band displacement. Can be a constant or a function
    :type dev_target: function or float
    :param band_target: Used for band displacement. Can be a constant or a function
    :type band_target: function or float
    :param center_target: Data column for the band center
    :type center_target: str
    """
    def return_function(data):
        if hasattr(band_target, "name") & hasattr(dev_target, "name"):
            column_name = f"lower_volatility_band_{c}_times_{band_target.name}&{dev_target.name}_under_{center_target.name}"
        elif hasattr(band_target, "name"):
            column_name = f"lower_volatility_band_{c}_times_{band_target.name}&{dev_target}_under_{center_target.name}"
        else:
            column_name = f"lower_volatility_band_{c}_times_{band_target}&{dev_target}_under_{center_target.name}"
        if column_name not in data.columns:
            data[column_name] = center_target - c * dev_target * band_target
        return data[column_name].copy()

    return return_function


def momentum(days=1, target="close"):
    """Calculates the momentum

    :param days: Window size, defaults to 1
    :type days: int, optional
    :param target: Data column to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"momentum_{days}_of_{target}"
        if column_name not in data.columns:
            data[column_name] = data[target].diff(periods=days)
        return data[column_name].copy()

    return return_function


def momentum_percentage(days=1, target="close"):
    """Calculates the momentum as a percentage

    :param days: Window size, defaults to 1
    :type days: int, optional
    :param target: Data colum to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"momentum_percentage_{days}_of_{target}"
        if column_name not in data.columns:
            data[column_name] = data[target].diff(periods=days)
            data.loc[days:, column_name] = data[column_name][days:].divide(
                data[target][: -1 * days].values
            )
        return data[column_name].copy()

    return return_function


def MACD_line(slow_trend=26, fast_trend=12):
    """Calculates the MACD line

    :param slow_trend: Slow window size, defaults to 26
    :type slow_trend: int, optional
    :param fast_trend: Fast window size, defaults to 12
    :type fast_trend: int, optional
    """
    def return_function(data):
        column_name = f"MACD_line_{slow_trend}/{fast_trend}"
        if column_name not in data.columns:
            slow_trend_data = exponential_smoothing(days_to_constant(slow_trend))(data)
            fast_trend_data = exponential_smoothing(days_to_constant(fast_trend))(data)
            data[column_name] = fast_trend_data - slow_trend_data
        return data[column_name].copy()

    return return_function


def MACD_signal(signal, slow_trend=26, fast_trend=12):
    """Calculates the MACD signal

    :param signal: Exponential smoothing window size of the MACD line
    :type signal: int
    :param slow_trend: Slow window size of MACD line, defaults to 26
    :type slow_trend: int, optional
    :param fast_trend: Fast windown size of MACD line, defaults to 12
    :type fast_trend: int, optional
    """
    def return_function(data):
        column_name = f"MACD_signal_{slow_trend}/{fast_trend}/{signal}"
        if column_name not in data.columns:
            macd_line = MACD_line(slow_trend, fast_trend, signal)(data)
            data[column_name] = exponential_smoothing(
                days_to_constant(signal), target=macd_line.name
            )(data)
        return data[column_name].copy()

    return return_function


def MACD_histogram(signal, slow_trend=26, fast_trend=12):
    """Calculates the MACD histogram

    :param signal: Exponential smoothing window size of the MACD line
    :type signal: int
    :param slow_trend: Slow window size of MACD line, defaults to 26
    :type slow_trend: int, optional
    :param fast_trend: Fast windown size of MACD line, defaults to 12
    :type fast_trend: int, optional
    """
    def return_function(data):
        column_name = f"MACD_histogram_{slow_trend}/{fast_trend}/{signal}"
        if column_name not in data.columns:
            macd_line = MACD_line(slow_trend, fast_trend)(data)
            macd_signal = MACD_signal(signal, slow_trend, fast_trend)(data)
            data[column_name] = macd_line - macd_signal
        return data[column_name].copy()

    return return_function


def divergence_index(slow_trend, fast_trend):
    """Calculates the divergence index

    :param slow_trend: Slow window size
    :type slow_trend: int
    :param fast_trend: Fast window size
    :type fast_trend: int
    """
    def return_function(data):
        column_name = f"divergence_index_{slow_trend}/{fast_trend}"
        if column_name not in data.columns:
            fast_trend_data = moving_average(fast_trend)(data)
            slow_trend_data = moving_average(slow_trend)(data)
            momentum_data = momentum()(data)
            data[column_name] = (fast_trend_data - slow_trend_data) / rolling_std(
                slow_trend, momentum_data.name
            )(data).pow(2)
        return data[column_name].copy()

    return return_function


def average_true_range(days=10, target="close"):
    """Calculates the average true range

    :param days: Window size, defaults to 10
    :type days: int, optional
    :param target: Data column to use, defaults to "close"
    :type target: str, optional
    """
    def return_function(data):
        column_name = f"average_true_range_{days}_of_{target}"
        high_col_name = f"high{target[5:]}"
        low_col_name = f"low{target[5:]}"
        if column_name not in data.columns:
            true_range = data[high_col_name] - data[low_col_name]
            data[column_name] = true_range.rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def stochastic_percentageK(days):
    """Calculates the stochastic K

    :param days: Window size
    :type days: int
    """
    def f(x):
        lowest = x["low"].nsmallest(1)
        highest = x["high"].max()
        return 100 * (x["close"].iloc[-1] - lowest) / (highest - lowest)

    def return_function(data):
        column_name = f"stochastic_percentageK_{days}"
        if column_name not in data.columns:
            data[column_name] = np.zeros(len(data))
            column_index = data.columns.get_loc(column_name)
            for i in range(len(data)):
                if i >= days - 1:
                    data.iloc[i, column_index] = f(
                        data.iloc[i - days + 1 : i + 1]
                    ).values
        return data[column_name].copy()

    return return_function


def stochastic_percentageD(days, daysK):
    """Calculates the stochastic D

    :param days: Window size
    :type days: int
    :param daysK: Window size for the stochastic K
    :type daysK: int
    """
    def return_function(data):
        column_name_K = f"stochastic_percentageK_{days}"
        column_name = f"stochastic_percentageD_{days}/{daysK}"
        if column_name not in data.columns:
            stochastic_percentageK(daysK)(data)
            data[column_name] = data[column_name_K].rolling(days).mean()
        return data[column_name].copy()

    return return_function


def ADoscillator():
    """Calculates the A/D oscillator"""
    def f(x):
        buying_power = x["high"] - x["open"]
        selling_power = x["close"] - x["low"]
        DRF = (buying_power + selling_power) / 2 / (x["high"] - x["low"])
        return DRF

    def return_function(data):
        column_name = "A/D_oscillator"
        if column_name not in data.columns:
            data[column_name] = f(data)
        return data[column_name].copy()

    return return_function


def percentageR(days):
    """Calculates the stochastic R
    
    :param days: Window size
    :type days: int
    """
    def f(x):
        highest = x["high"].max()
        lowest = x["low"].min()
        buying_power = highest - x["close"].iloc[-1]
        return buying_power / (highest - lowest)

    def return_function(data):
        column_name = f"percentageR_{days}"
        if column_name not in data.columns:
            data[column_name] = np.zeros(len(data))
            column_index = data.columns.get_loc(column_name)
            for i in range(len(data)):
                if i >= days - 1:
                    data.iloc[i, column_index] = f(data.iloc[i - days + 1 : i + 1])
        return data[column_name].copy()

    return return_function


def RSI(days):
    """Calculates the RSI

    :param days: Window size
    :type days: int
    """
    def f():
        def g(x):
            AU = x[x > 0].sum()
            AD = -x[x < 0].sum()
            if AD == 0:
                return 100
            else:
                RS = AU / AD
                return 100 - (100 / (1 + RS))

        return g

    def return_function(data):
        column_name = f"RSI_{days}"
        if column_name not in data.columns:
            mom_name = momentum()(data).name
            data[column_name] = (
                data[mom_name].rolling(window=days).apply(f(), raw=False)
            )
        return data[column_name].copy()

    return return_function


def special_k():
    """Calculates the special k indicator"""
    def return_function(data):
        column_name = "special_k"
        if column_name not in data.columns:
            momentum_days = [10, 15, 20, 30, 40, 65, 75, 100, 195, 265, 390, 530]
            moving_average_days = [10, 10, 10, 15, 50, 65, 75, 100, 130, 130, 130, 195]
            weighted_average_multiplier = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
            # Creating all the momentums and moving averages in advance
            ma_names = [
                moving_average(days=ma, target=momentum(days=mom)(data).name)(data).name
                for mom, ma in zip(momentum_days, moving_average_days)
            ]

            data[column_name] = 0
            column_name_pos = data.columns.get_loc(column_name)
            for i in range(0, len(data)):
                data.iloc[i, column_name_pos] = (
                    sum(
                        [
                            weight * data.iloc[i, data.columns.get_loc(ma_name)]
                            for ma_name, weight in zip(
                                ma_names, weighted_average_multiplier
                            )
                        ]
                    )
                    / 30
                )

        return data[column_name].copy()

    return return_function
