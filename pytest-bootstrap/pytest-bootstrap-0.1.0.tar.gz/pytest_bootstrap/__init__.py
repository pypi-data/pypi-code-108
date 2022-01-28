import numpy as np
import typing
import warnings


class BootstrapTestError(RuntimeError):
    """
    Reference value falls outside bootstrapped confidence interval.
    """
    pass


def bootstrap_test(samples: np.ndarray, statistic: typing.Callable, reference: float,
                   statistic_args: typing.Iterable = None, statistic_kwargs: typing.Mapping = None,
                   num_bootstrap_samples: int = 1000,
                   alpha: float = 1e-2) -> dict:
    """
    Compare a bootstrap sample of a :attr:`statistic` evaluated on i.i.d :attr:`samples` from a
    stochastic process with a :attr:`reference` value.

    The test will fail if the :attr:`reference` lies outside the :code:`1 - alpha` posterior
    interval, i.e. is smaller than the empirical :code:`alpha / 2` quantile or larger than the
    :code:`1 - alpha / 2` quantile.

    Args:
        samples: I.i.d. samples from a stochastic process on which to evaluate the
            :attr:`statistic`.
        statistic: Function to evaluate a statistic on a bootstrapped sample.
        reference: Reference value to compare with the bootstrap sample of the :attr:`statistic`.
        statistic_args: Positional arguments forwarded to the :attr:`statistic`.
        statistic_kwargs: Keyword arguments forwarded to the :attr:`statistic`.
        num_bootstrap_samples: Number of bootstrap samples.
        alpha: Significance level to use for testing agreement between the bootstrapped distribution
            of the :attr:`statistic` and the :attr:`reference` value. :attr:`alpha` roughly
            corresponds to the probability that the test will fail even if the :attr:`reference`
            value is correct. This value should be small for the test to pass with high probability.
        ax: Axes for plotting the bootstrap distribution if desired.

    Returns:
        result: Dictionary of test information, comprising

            - :attr:`lower` -- Lower limit of the :code:`1 - alpha` bootstrapped interval, i.e. the
              :code:`alpha / 2` quantile.
            - :attr:`upper` -- Upper limit of the :code:`1 - alpha` bootstrapped interval, i.e. the
              :code:`1 - alpha / 2` quantile.
            - :attr:`iqr` -- Interquartile range of the bootstrapped :attr:`statistic`.
            - :attr:`median` -- Median of the bootstrapped :attr:`statistic`.
            - :attr:`z_score` -- Z-score of the :attr:`reference` value under the bootstrapped
              distribution, i.e. :code:`(reference - mean(s)) / std(s)`, where :attr:`s` is the
              vector of bootstrapped :attr:`statistic`.

    """
    if alpha < 1 / num_bootstrap_samples:
        warnings.warn('cannot estimate tail probabilities smaller than `1 / (num_bootstrap_samples '
                      f'= {num_bootstrap_samples})', UserWarning)

    statistic_args = statistic_args or ()
    statistic_kwargs = statistic_kwargs or {}

    # Evaluate the bootstrapped statistics.
    samples = np.asarray(samples)
    statistics = []
    for _ in range(num_bootstrap_samples):
        idx = np.random.choice(samples.shape[0], samples.shape[0])
        bootstrap_sample = samples[idx]
        statistics.append(statistic(bootstrap_sample, *statistic_args, **statistic_kwargs))
    statistics = np.asarray(statistics)

    # Evaluate the interval.
    lower, upper = np.percentile(statistics, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    # Collect summary information.
    result = {
        'alpha': alpha,
        'reference': reference,
        'lower': lower,
        'upper': upper,
        'z_score': (reference - np.mean(statistics)) / np.std(statistics),
        'median': np.median(statistics),
        'iqr': np.diff(np.percentile(statistics, [25, 75])).squeeze(),
    }

    # Fail the test if the p-value is smaller than the desired significance level.
    if reference < lower or reference > upper:
        raise BootstrapTestError(result)
    result['statistics'] = statistics
    return result
