# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Binning regression dataset targets to be used in chart metrics."""
import logging
import math
import numpy as np

from typing import Any, Dict, Tuple

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared._cv_splits import _CVType


logger = logging.getLogger(__name__)

# Number of bins should be kept reasonable for a visualization
_MIN_N_BINS = 1
_MAX_N_BINS = 100

# Maximum attempts at doubling the precision
_SKEW_MAX_PRECISION = 32

# How much of an effect the biased value will have on the middle bin's boundaries
# Given a, x, b and weight of 19, the boundaries are [0.05a + 0.95x, 0.95x + 0.05b] before rounding
_SKEW_WEIGHT = 19

# Keys must remain the same for back-compat
_N_BINS_KEY = 'number_of_bins'
_STARTS_KEY = 'bin_starts'
_ENDS_KEY = 'bin_ends'


def get_dataset_bins(cv_splits, X, y):
    cv_split_type = cv_splits.get_cv_split_type()
    split_indices = cv_splits.get_cv_split_indices()
    k_folds = cv_splits.get_num_k_folds()
    valid_fraction = cv_splits.get_fraction_validation_size()

    n_samples = int(X.shape[0]) if X is not None else None

    if cv_split_type == _CVType.KFoldCrossValidationSplit:
        n_valid = n_samples // k_folds
        bin_info = make_dataset_bins(n_valid, y, percentile=1)
    elif cv_split_type == _CVType.TestCutoffCVSplit:
        n_valid = int(n_samples * valid_fraction / k_folds)
        bin_info = make_dataset_bins(n_valid, y, percentile=1)
    elif cv_split_type == _CVType.MonteCarloCrossValidationSplit:
        n_valid = int(n_samples * valid_fraction)
        bin_info = make_dataset_bins(n_valid, y, percentile=1)
    elif cv_split_type == _CVType.CustomCrossValidationSplit:
        # We know exactly which data will be used for validation,
        # so we pass only y values in the custom validation splits
        tot_indices = [ind for split in split_indices for ind in split[1]]
        tot_y = y[np.unique(tot_indices)]
        bin_info = make_dataset_bins(len(tot_indices), tot_y, percentile=1)
    elif cv_split_type == _CVType.TimeSeriesSplit:
        full_indices = [ind for split in split_indices for ind in split[1]]
        # Ideally we would use `tot_y = y[np.unique(full_indices)]`
        # However, splits are based on the raw data while `y` contains transformed data,
        # which may have been expended based on timeseries featurizers.
        # Instead we take the values from the generated splits
        y_full = np.concatenate(
            [split._recover_from_cache_store()._y_test for split in cv_splits._featurized_cv_splits]
        )
        bin_info = make_dataset_bins(len(full_indices), y_full, percentile=1)
    else:
        n_valid = int(n_samples * valid_fraction)
        bin_info = make_dataset_bins(n_valid, y, percentile=1)

    return bin_info


def make_dataset_bins(n_valid: int, y: np.ndarray, percentile: float = 1.0) -> Dict[str, Any]:
    """
    Compute bins based on the full dataset targets.

    First and last bins hold all outliers of y. These outlier bins are used
        to make the histogram more readable for the user. The default edges
        of the outlier bins are the 1st and 99th percentiles of y.
    The number of bins is selected to keep the amount of data in each bin
        at 10 samples on average. The number of bins is capped at 100, which
        becomes important for large validation sets. The size of metrics
        computed using bin info will not continue to grow with the size of
        the dataset indefinitely.

    :param n_valid: Number of points in validation set which will be binned.
    :param y: Target values used to determine the range of the bins.
    :param percentile: Percentile to use for outlier bins. This percentile
        will be ignored if data skew causes all points to end up in an
        outlier bin.
    :return: A dictionary with keys: number_of_bins, bin_starts, bin_ends
        Information about how to discretize the regression target feature.
        Used to standardize the bin edges of chart metrics when aggregating
        over many cross validation folds with different data distributions.
    """
    Contract.assert_true(
        n_valid > 0,
        message="Number of validation points must be greater than 0.",
        target="_dataset_binning.make_dataset_bins.n_valid", log_safe=True)

    Contract.assert_true(
        y.shape[0] != 0,
        message="y must not be empty.",
        target="_dataset_binning.make_dataset_bins.y.shape", log_safe=True)

    y_unique = np.unique(y)
    if y_unique.shape[0] == 1:
        return _create_info_dict(1, np.array([y[0]]), np.array([y[0]]))

    try:
        # Determine the number of bins and the positions of outlier bins
        first_end, last_start = np.percentile(y, [percentile, 100 - percentile])
        if first_end == last_start:
            first_end, last_start, n_bins = _fix_skewed_outliers(first_end, last_start, y)
        else:
            n_bins = math.ceil(math.sqrt(n_valid))
            if n_bins < _MIN_N_BINS:
                n_bins = _MIN_N_BINS
            elif n_bins > _MAX_N_BINS:
                n_bins = _MAX_N_BINS

        # Compute evenly spaced bins between outlier bins
        inner_edges = np.linspace(first_end, last_start, n_bins - 1)
        bin_width = (last_start - first_end) / n_bins

        # Round bin edges so UI does not have to
        inner_edges = [_round_bin_edge(edge, bin_width) for edge in inner_edges]
        first_start = _round_bin_edge(y.min(), bin_width, direction='down')
        last_end = _round_bin_edge(y.max(), bin_width, direction='up')
        bin_edges = np.r_[first_start, inner_edges, last_end]

        # Remove bins with width zero
        bin_edges = np.unique(bin_edges)
        n_bins = bin_edges.shape[0] - 1
    except Exception as e:
        dimensions = {
            'y': y.shape,
            'y_unique': y_unique.shape,
            'n_valid': n_valid
        }
        logger.error("Failed to bin dataset with dimensions {}".format(dimensions))
        logging_utilities.log_traceback(e, logger, is_critical=False)
        return _create_info_dict(1, np.array([y.min()]), np.array([y.max()]))

    Contract.assert_true(
        n_bins != 0,
        message="Could not create bins based on y.",
        target="_dataset_binning.make_dataset_bins.n_bins", log_safe=True)

    return _create_info_dict(n_bins, bin_edges[:-1], bin_edges[1:])


def _create_info_dict(n_bins: int, starts: np.ndarray, ends: np.ndarray) -> Dict[str, Any]:
    """
    Create bin info dict.

    :param n_bins: Total number of bins.
    :param starts: Starts of bins.
    :param ends: Ends of bins.
    :return: Dict containing the bin info.
    """
    return {
        _N_BINS_KEY: n_bins,
        _STARTS_KEY: starts,
        _ENDS_KEY: ends,
    }


def _fix_skewed_outliers(first_end: float, last_start: float, y: np.ndarray) -> Tuple[float, float, int]:
    """
    Compute outlier bins when data is skewed.

    When data is extremely skewed the first percentile may not be sufficiently
        small to differ from the 99th percentile. This function successively
        halves the percentile until we can guarantee a middle bin.

    :param first_end: First bin end of the bin edges (end of left outlier bin).
    :param last_start: Last bin start of the bin edges (start of right outlier bin).
    :param y: Target feature.
    :return: Tuple of (updated first_end, updated last_start, updated n_bins)
    """
    p = [1 / (2 ** i) for i in range(_SKEW_MAX_PRECISION)] + [0]
    candidates = np.percentile(y, p, interpolation='lower')
    for candidate in candidates:
        if candidate != first_end:
            first_end = (first_end * _SKEW_WEIGHT + candidate) / (_SKEW_WEIGHT + 1)
            break

    p = [100 - 1 / (2 ** i) for i in range(_SKEW_MAX_PRECISION)] + [100]
    candidates = np.percentile(y, p, interpolation='higher')
    for candidate in candidates:
        if candidate != last_start:
            last_start = (last_start * _SKEW_WEIGHT + candidate) / (_SKEW_WEIGHT + 1)
            break

    n_bins = 3  # n_bins = 3 works in all cases here
    return first_end, last_start, n_bins


def _round_bin_edge(edge: float, bin_width: float, decimals: int = 2, direction: str = 'nearest') -> np.float:
    """
    Round a bin edge so that it displays well in a UI.

    :param edge: The float value of one bin edge
    :param bin_width: The width of bins to give the magnitude of edges
    :param direction: The direction to round
        'nearest' rounds to the nearest value
        'up' rounds up
        'down' rounds down
    :return: The float value of the new rounded edge
    """
    Contract.assert_true(
        bin_width > 0,
        message="bin_width must be greater than 0.",
        target="_dataset_binning._round_bin_edge.bin_width", log_safe=True)

    Contract.assert_true(
        direction in ['nearest', 'up', 'down'],
        message="direction must be 'nearest', 'up', or 'down'.",
        target="_dataset_binning._round_bin_edge.direction", log_safe=True)

    log_magnitude = -1 * int(np.log10(bin_width)) + decimals
    if direction == 'nearest':
        if bin_width >= 1:
            return np.around(edge, decimals=decimals)
        else:
            return np.around(edge, decimals=log_magnitude)
    else:
        round_func = np.ceil if direction == 'up' else np.floor
        mult = 10 ** log_magnitude
        return np.around(round_func(edge * mult) / mult, decimals=log_magnitude)
