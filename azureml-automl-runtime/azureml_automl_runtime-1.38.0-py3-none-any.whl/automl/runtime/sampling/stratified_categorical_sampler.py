# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stratified sampler."""
from typing import Any, List, Optional, Tuple, Union
import logging

import math
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.runtime.shared.types import CoreDataInputType, CoreDataSingleColumnInputType
from . import AbstractSampler, IndexSplittingConfig


logger = logging.getLogger(__name__)


class StratifiedCategoricalSampler(AbstractSampler):
    """
    Stratified sampler for columns that are *conceptually* categorical,
    typically to be used for CVTE experiments. Note that this sampler may
    be used on some columns that do not have "categorical" purposes as
    detected by AutoML.

    As opposed to the CountSampler, which provides a random sample regardless
    of the column composition, this sampler tries to preserve the relative
    cardinalities of the categories to be passed in for sweeping.
    """

    def __init__(self,
                 seed: int,
                 max_rows: int = 10000,
                 is_constraint_driven: bool = True,
                 task: str = constants.Tasks.REGRESSION,
                 train_frac: Optional[float] = None,
                 max_full_cat_default: int = 50,
                 category_occurrence_minimum: int = 15,
                 *args: Any, **kwargs: Any) -> None:
        """
        Initialize sampler.

        :param seed: Random seed to use to sample.
        :param max_rows: Maximum rows to output.
        :param is_constraint_driven: Is the sweeping process constraint driven or not.
        :param task: The task type corresponding to this sweeping experiment.
        :param train_frac: Fraction of data to be considered for training.
        :param max_full_cat_default: The (soft) maximum number of categories we will include in the sample, if we can
        fully fill it while maintaining the same proportionality.
        :param category_occurrence_minimum: The absolute number of occurrences of a category that we will use
        for thresholding to build our sample.
        """
        super(StratifiedCategoricalSampler, self).__init__(seed=seed,
                                                           task=task,
                                                           max_rows=max_rows,
                                                           is_constraint_driven=is_constraint_driven,
                                                           train_frac=train_frac)
        self._max_full_cat_default = max_full_cat_default
        self._category_occurrence_minimum = category_occurrence_minimum

    @staticmethod
    def _get_cat_wise_sample_nums(most_frequent_cats: pd.Series,
                                  num_sample: int, train_frac: float, test_frac: float) -> Tuple[List[int], List[int]]:
        """
        Calculate lists of train/test sample numbers to satisfy the specified train_frac/test_frac/num_sample
        requirements.

        :param most_frequent_cats: The top K most frequent categories from the input data. There should be enough
        entries in this collection to populate the requested number of samples.
        :param num_sample: How many samples we want.
        :param train_frac: The fraction of the entire dataset we want in our sweeping training sample.
        :param test_frac: The fraction of the entire dataset we want in our sweeping test sample.
        :return: Two lists, one for the training sample numbers per category (as ints), and one for test (likewise).
        """
        num_sample_train = math.ceil(num_sample * train_frac / (train_frac + test_frac))
        num_sample_test = math.floor(num_sample * test_frac / (train_frac + test_frac))

        train_sample_nums = (most_frequent_cats / most_frequent_cats.sum() * num_sample_train).astype(int)
        test_sample_nums = (most_frequent_cats / most_frequent_cats.sum() * num_sample_test).astype(int)

        total_train_amt_remaining = num_sample_train - train_sample_nums.sum()
        i = 0
        while total_train_amt_remaining > 0:
            cat_leftover = most_frequent_cats.iloc[i] - train_sample_nums.iloc[i] - test_sample_nums.iloc[i]
            if cat_leftover >= total_train_amt_remaining:
                train_sample_nums.iloc[i] += total_train_amt_remaining
                total_train_amt_remaining = 0
            elif cat_leftover > 0:
                train_sample_nums.iloc[i] += cat_leftover
                total_train_amt_remaining -= cat_leftover
            i += 1

        total_test_amt_remaining = num_sample_test - test_sample_nums.sum()
        i = 0
        while total_test_amt_remaining > 0:
            cat_leftover = most_frequent_cats.iloc[i] - test_sample_nums.iloc[i] - train_sample_nums.iloc[i]
            if cat_leftover >= total_test_amt_remaining:
                test_sample_nums.iloc[i] += total_test_amt_remaining
                total_test_amt_remaining = 0
            elif cat_leftover > 0:
                test_sample_nums.iloc[i] += cat_leftover
                total_test_amt_remaining -= cat_leftover
            i += 1

        for cat in train_sample_nums.index:
            # Ensure we don't have an all or nothing split, which will cause sklearn to fail.
            if not test_sample_nums[cat]:
                if train_sample_nums[cat] > 1:  # Has one to spare, so we adjust to maintain the total.
                    train_sample_nums[cat] -= 1
                test_sample_nums[cat] += 1
            # We don't expect a test_frac > train_frac case currently, but better to be safe.
            if not train_sample_nums[cat]:
                if test_sample_nums[cat] > 1:
                    test_sample_nums[cat] -= 1
                train_sample_nums[cat] += 1

        return train_sample_nums, test_sample_nums

    def _sample_high_frequency_categories(self,
                                          X: pd.Series,
                                          y: CoreDataSingleColumnInputType,
                                          train_frac: float, test_frac: float) \
            -> Tuple[pd.Series, pd.Series, np.ndarray, np.ndarray]:
        """
        We break our sampling into two parts, where we treat the high and low frequency categories differently. This
        function samples from the overall input over the high frequency categories.

        :param X: Input data column
        :param y: Output label.
        :param train_frac: Overall fraction of the data we want in the training set for our sweeping sample.
        :param test_frac: Overall fraction of the data we want in the test set for our sweeping sample.
        :return: Tuple of highf_X_train_sample, highf_X_test_sample, highf_y_train_sample, highf_y_test_sample.
        """
        sample_fraction = min(train_frac + test_frac, 1)

        counts = X.value_counts()
        high_thresholded_counts = counts[counts >= self._category_occurrence_minimum]
        total_high_thresholded = high_thresholded_counts.sum()

        # No sampling needed.
        if min(train_frac, test_frac) * total_high_thresholded < 1:
            return pd.Series(), pd.Series(), np.empty(0), np.empty(0)

        # Determine how many samples we want from the frequent categories.
        num_sample_high = int(total_high_thresholded * sample_fraction + 0.5)

        if sample_fraction < 1:
            most_frequent_cats = high_thresholded_counts.head(min(self._max_full_cat_default,
                                                                  math.ceil(num_sample_high * min(train_frac,
                                                                                                  test_frac))))
            if most_frequent_cats.sum() < num_sample_high:
                # If the top K categories are not frequent enough to populate the required sample, we will add more in
                # order of frequency until this condition is met. Note we know it is guaranteed that we can satisfy
                # this condition eventually based on the definition of num_sample_high and the fact that
                # sample_fraction is guaranteed to be less than 1.
                curr_total = most_frequent_cats.sum()
                added_example_total = 0
                items_to_add = {}  # Maintain separate container for efficiency.
                i = self._max_full_cat_default
                while curr_total + added_example_total < num_sample_high:
                    i += 1
                    new_cat_freq = high_thresholded_counts.iloc[i]
                    items_to_add[high_thresholded_counts.index[i]] = new_cat_freq
                    added_example_total += new_cat_freq
                most_frequent_cats = most_frequent_cats.append(pd.Series(items_to_add))

            # Fraction was previously N_sample / N_input. Now that we've truncated the input, we must scale the frac.
            # (N_sample / N_input) * (N_input / N_subset) = N_sample / N_subset
            train_frac *= total_high_thresholded / most_frequent_cats.sum()
            test_frac *= total_high_thresholded / most_frequent_cats.sum()

            # ...and fix any rounding errors.
            overflow = train_frac + test_frac - 1
            train_frac -= max(overflow / 2, 0)
            test_frac -= max(overflow / 2, 0)
        else:
            # No need to down-sample, so we already have our most frequent category collection.
            most_frequent_cats = high_thresholded_counts

        # We know that the number of categories is <= our sample requirement, so we can use built-in sklearn methods.
        highf_X, highf_y = X[X.isin(most_frequent_cats.index)], y[X.isin(most_frequent_cats.index)]
        attempt_stratify_by_target = highf_y if self._task == constants.Tasks.CLASSIFICATION else None
        if attempt_stratify_by_target is None:
            X_highf_train_sample, X_highf_test_sample, y_highf_train_sample, y_highf_test_sample = \
                train_test_split(highf_X, highf_y,
                                 train_size=train_frac, test_size=test_frac,
                                 random_state=self._seed, stratify=highf_X)
        else:
            # See if we can stratify according to the classes *as well*, but we will give priority to the
            # categories when this is not possible.
            cat_wise_train_sample_nums, cat_wise_test_sample_nums = \
                StratifiedCategoricalSampler._get_cat_wise_sample_nums(most_frequent_cats, num_sample_high,
                                                                       train_frac, test_frac)
            cat_wise_highf_train_samples = []
            cat_wise_highf_test_samples = []
            for cat in most_frequent_cats.index:
                cat_indices = highf_X == cat
                cat_targets_of_interest = highf_y[cat_indices]
                # On average, faster to check first than to try and recover if failure case is more common.
                _, target_counts = np.unique(cat_targets_of_interest, return_counts=True)
                if target_counts.min() <= 1 or len(target_counts) > min(cat_wise_train_sample_nums[cat],
                                                                        cat_wise_test_sample_nums[cat]):
                    # Stratified sampling will fail, so don't try it.
                    (X_highf_cat_wise_train_sample, X_highf_cat_wise_test_sample,
                     y_highf_cat_wise_train_sample, y_highf_cat_wise_test_sample) = \
                        train_test_split(highf_X[cat_indices], cat_targets_of_interest,
                                         train_size=cat_wise_train_sample_nums[cat],
                                         test_size=cat_wise_test_sample_nums[cat],
                                         random_state=self._seed)
                else:
                    (X_highf_cat_wise_train_sample, X_highf_cat_wise_test_sample,
                     y_highf_cat_wise_train_sample, y_highf_cat_wise_test_sample) = \
                        train_test_split(highf_X[cat_indices], cat_targets_of_interest,
                                         train_size=cat_wise_train_sample_nums[cat],
                                         test_size=cat_wise_test_sample_nums[cat],
                                         random_state=self._seed,
                                         stratify=cat_targets_of_interest)
                cat_wise_highf_train_samples.append((X_highf_cat_wise_train_sample, y_highf_cat_wise_train_sample))
                cat_wise_highf_test_samples.append((X_highf_cat_wise_test_sample, y_highf_cat_wise_test_sample))

            X_highf_train_sample = pd.concat([X_sample for X_sample, _ in cat_wise_highf_train_samples])
            y_highf_train_sample = np.concatenate([y_sample for _, y_sample in cat_wise_highf_train_samples])
            X_highf_test_sample = pd.concat([X_sample for X_sample, _ in cat_wise_highf_test_samples])
            y_highf_test_sample = np.concatenate([y_sample for _, y_sample in cat_wise_highf_test_samples])

        return (X_highf_train_sample, X_highf_test_sample,
                y_highf_train_sample, y_highf_test_sample)

    def _sample_low_frequency_categories(self,
                                         X: pd.Series,
                                         y: CoreDataSingleColumnInputType,
                                         train_frac: float, test_frac: float) \
            -> Tuple[pd.Series, pd.Series, np.ndarray, np.ndarray]:
        """
        We break our sampling into two parts, where we treat the high and low frequency categories differently. This
        function samples from the overall input over the low frequency categories.

        :param X: Input data column.
        :param y: Output label.
        :param train_frac: Overall fraction of the data we want in the training set for our sweeping sample.
        :param test_frac: Overall fraction of the data we want in the test set for our sweeping sample.
        :return: Tuple of lowf_X_train_sample, lowf_X_test_sample, lowf_y_train_sample, lowf_y_test_sample.
        """
        counts = X.value_counts()
        low_thresholded_counts = counts[counts < self._category_occurrence_minimum]

        # No sampling needed.
        if min(train_frac, test_frac) * low_thresholded_counts.sum() < 1:
            return pd.Series(), pd.Series(), np.empty(0), np.empty(0)

        # Get sample from low frequency categories
        lowf_X, lowf_y = X[X.isin(low_thresholded_counts.index)], y[X.isin(low_thresholded_counts.index)]
        attempt_stratify_by_target = lowf_y if self._task == constants.Tasks.CLASSIFICATION else None
        try:
            X_lowf_train_sample, X_lowf_test_sample, y_lowf_train_sample, y_lowf_test_sample = \
                train_test_split(lowf_X, lowf_y,
                                 train_size=train_frac, test_size=test_frac,
                                 random_state=self._seed, stratify=attempt_stratify_by_target)
        except ValueError:
            X_lowf_train_sample, X_lowf_test_sample, y_lowf_train_sample, y_lowf_test_sample = \
                train_test_split(lowf_X, lowf_y,
                                 train_size=train_frac, test_size=test_frac,
                                 random_state=self._seed)
        return (X_lowf_train_sample, X_lowf_test_sample,
                y_lowf_train_sample, y_lowf_test_sample)

    def sample(self, X: pd.DataFrame,
               y: CoreDataSingleColumnInputType,
               cols: Optional[Union[str, List[str]]] = None) \
            -> Tuple[CoreDataInputType, CoreDataSingleColumnInputType, IndexSplittingConfig]:
        """
        Get a stratified sample of the input column(s).

        :param X: Input data.
        :param y: Output label.
        :param cols: The input column over which we should sample.
        :return: Sampled data.
        """
        if cols is None or isinstance(cols, list) or cols not in X.columns:  # Note we expect a single column.
            raise ClientException("stratified categorical sampler passed missing or invalid column", has_pii=False)
        X = X[cols]

        n_rows = np.shape(X)[0]
        train_frac, test_frac = self._get_train_test_frac(n_train=self._max_rows, n_rows=n_rows)
        logger.debug("Feature sweeping sampling: train_frac = {}, test_frac={}".format(train_frac, test_frac))

        (lowf_X_train_sample, lowf_X_test_sample,
         lowf_y_train_sample, lowf_y_test_sample) = self._sample_low_frequency_categories(X, y,
                                                                                          train_frac, test_frac)

        (highf_X_train_sample, highf_X_test_sample,
         highf_y_train_sample, highf_y_test_sample) = self._sample_high_frequency_categories(X, y,
                                                                                             train_frac, test_frac)

        X_train_sample, y_train_sample = shuffle(pd.concat((highf_X_train_sample, lowf_X_train_sample)),
                                                 np.concatenate((highf_y_train_sample, lowf_y_train_sample)),
                                                 random_state=self._seed)

        X_test_sample, y_test_sample = shuffle(pd.concat((highf_X_test_sample, lowf_X_test_sample)),
                                               np.concatenate((highf_y_test_sample, lowf_y_test_sample)),
                                               random_state=self._seed)

        # Now, do final concatenation to get overall X, y samples, and preserve train/test splits that we have
        # carefully created by specifying an IndexSplittingConfig as opposed to the traditional SplittingConfig.
        X_sampled = pd.concat((X_train_sample, X_test_sample))
        y_sampled = np.concatenate((y_train_sample, y_test_sample))
        train_cnt, test_cnt = X_train_sample.shape[0], X_test_sample.shape[0]
        split_config = IndexSplittingConfig(train_idxs=np.arange(train_cnt),
                                            test_idxs=np.arange(train_cnt, train_cnt + test_cnt),
                                            task=self._task)

        return X_sampled, y_sampled, split_config
