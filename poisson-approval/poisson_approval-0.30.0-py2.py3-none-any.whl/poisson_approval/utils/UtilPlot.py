from math import sqrt
import numpy as np
from matplotlib import pyplot as plt


def plt_plot_with_error(x, y, n_samples, **kwargs):
    """
    Adaptation of ``plt.plot`` for Monte-Carlo experiments, with error area.

    We assume that y-values are obtained by a Monte-Carlo method on a random variable that is in [0, 1]. The margin of
    error is then bounded by the one of a repeated Bernouilli of parameter 0.5, which is itself approximated by a
    normal distribution. Hence the 95% confidence interval is approximately ± 1 / sqrt(n_samples). Note that this
    confidence interval is also valid (only overestimated) when the y-value is 0 or 1.

    Parameters
    ----------
    x : array-like
        The x-data.
    y : array-like
        The y-data. Values must be in [0, 1].
    n_samples : int
        Number of samples used for Monte-Carlo.
    kwargs
        Other keyword arguments are passed to the function ``plot`` of `matplotlib`.

    Examples
    --------
        >>> x = np.arange(0, 1, .1)
        >>> y = np.random.random(10)
        >>> plt_plot_with_error(x, y, n_samples=100)
    """
    error = 1 / sqrt(n_samples)
    plt.fill_between(x,
                     np.maximum(np.array(y, dtype=float) - error, 0),
                     np.minimum(np.array(y, dtype=float) + error, 1),
                     color='silver')
    plt.plot(x, y, **kwargs)


def plt_step_with_error(x, y, n_samples, **kwargs):
    """
    Adaptation of ``plt.step`` for Monte-Carlo experiments, with error area.

    We assume that y-values are obtained by a Monte-Carlo method on a random variable that is in [0, 1]. The margin of
    error is then bounded by the one of a repeated Bernouilli of parameter 0.5, which is itself approximated by a
    normal distribution. Hence the 95% confidence interval is approximately ± 1 / sqrt(n_samples). Note that this
    confidence interval is also valid (only overestimated) when the y-value is 0 or 1.

    Parameters
    ----------
    x : array-like
        The x-data.
    y : array-like
        The y-data. Values must be in [0, 1].
    n_samples : int
        Number of samples used for Monte-Carlo.
    kwargs
        Other keyword arguments are passed to the function ``step`` of `matplotlib`.

    Examples
    --------
        >>> x = np.arange(0, 1, .1)
        >>> y = np.random.random(10)
        >>> plt_step_with_error(x, y, n_samples=100)
    """
    error = 1 / sqrt(n_samples)
    plt.fill_between(x,
                     np.maximum(np.array(y, dtype=float) - error, 0),
                     np.minimum(np.array(y, dtype=float) + error, 1),
                     color='silver')
    plt.step(x, y, **kwargs)


def plt_cdf(data, weights, n_samples, data_min=0, data_max=1, **kwargs):
    """
    Plot a cumulative distribution function from Monte-Carlo experiments, with error area.

    We assume that the values in `data` are obtained by a Monte-Carlo method on a random variable that is in
    `[data_min, data_max]`. For the confidence interval, cf. :meth:`plt_step_with_error`.

    Parameters
    ----------
    data : array-like
        Each encountered value.
    weights : array-like
        The weight (probability) with which the value was encountered.
    n_samples : int
        Number of samples used for Monte-Carlo.
    data_min : Number
        Minimum possible value of `data`. Default: 0.
    data_max : Number
        Maximum possible value of `data`. Default: 1.
    kwargs
        Other keyword arguments are passed to the function ``step`` of `matplotlib`.

    Examples
    --------
        >>> data = np.random.random(100)
        >>> weights = np.ones(100) / 100
        >>> plt_cdf(data, weights, n_samples=100)
    """
    data_weights_sorted = sorted(zip(data, weights))
    data_sorted = [d for d, _ in data_weights_sorted]
    weights_sorted = [w for _, w in data_weights_sorted]
    weights_cum = np.cumsum(weights_sorted)
    plt_step_with_error([data_min] + data_sorted + [data_max], [0] + list(weights_cum) + [1], n_samples, **kwargs)
