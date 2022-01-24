# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""One-hot encoding for categorical columns."""
from typing import Any, List
from warnings import warn, catch_warnings, simplefilter
import logging

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDfMissingColumn,
    InvalidArgumentType)
from azureml.automl.core.shared.exceptions import UntrainedModelException
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingDataException)
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.shared import forecasting_verify as verify
from .forecasting_base_estimator import AzureMLForecastTransformerBase


class CategoryBinarizer(AzureMLForecastTransformerBase):
    """A transformer produces binary columns from a TimeSeriesDataFrame.

    Also known as "One-Hot Encoding" or "Dummy Coding."
    """

    def __init__(self, prefix=None, prefix_sep='_', dummy_na=False,
                 columns=None, encode_all_categoricals=False,
                 drop_first=False):
        """
         Construct a category binarizer.

        :param prefix:
        String to append to DataFrame column names that are
        categorically coded. Can also be a list with  length equal
        to the number of columns or a dictionary mapping column
        names to prefixes.
        :type prefix:  string, list of strings, or dict of strings, default None

        :param prefix_sep: If appending prefix, separator/delimiter to use.
        :type prefix_sep: str, default '_'

        :param dummy_na: add a column to indicate NaNs, if False NaNs are ignored
        :type dummy_na: bool

        :param columns:
            Column names in the DataFrame to be encoded.
            These are columns that should be considered categorical.
            If columns=None then all the columns with `object` or `category` dtype
            will be encoded.
        :type columns: list-like, default None

        :param encode_all_categoricals:
            Detect and encode any columns in an input that have `object` or
            `category` dtype in addition to columns explicitly listed in the
            `columns` parameter.

            This option is useful when a `CategoryBinarizer`
            follows other transforms that may produce new categorical columns
            In this case, it may be difficult to know what the names of these
            columns will be prior to fit time.
        :type encode_all_categoricals: bool

        :param drop_first:
            Whether to get k-1 dummies out of k categorical levels
            by removing the first level
        :type drop_first: bool
        """
        self.prefix = prefix
        self.prefix_sep = prefix_sep
        self.dummy_na = dummy_na
        self.columns = columns
        self.encode_all_categoricals = encode_all_categoricals
        self.drop_first = drop_first

        self._is_fit = False
        self._detected_cols = []  # type: List[Any]

    @property
    def columns(self):
        """
        Names of columns to consider as categorical.

        If columns=None then all the columns with `object` or `category` dtype
        will be encoded.
        """
        return self._columns

    @columns.setter
    def columns(self, vals):
        if verify.is_iterable_but_not_string(vals):
            if all(isinstance(c, str) for c in vals):
                # Cast to set to remove duplicates
                self._columns = sorted(list(set(vals)))
            else:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(InvalidArgumentType, target='columns',
                                        reference_code=ReferenceCodes._TS_TRANS_INVALID_TYPE_OF_COLUMN_NAMES,
                                        argument="vals",
                                        actual_type=', '.join([str(type(c)) for c in vals]),
                                        expected_types="None, str, List[str]")
                )
        elif isinstance(vals, str):
            self._columns = [vals]
        elif vals is None:
            self._columns = []
        else:
            raise ForecastingDataException._with_error(
                AzureMLError.create(InvalidArgumentType, target='columns',
                                    reference_code=ReferenceCodes._TS_TRANS_INVALID_TYPE_OF_COL_NAME,
                                    argument="vals",
                                    actual_type=type(vals),
                                    expected_types="None, str, List[str]")
            )

    @property
    def columns_in_fit(self):
        """
        Read-only property containing list of encoded columns from last fit.

        There are situations where columns_in_fit and columns are different.
        For instance, if columns=None when fit is called, fit will save
        a list of all columns with dtyp=object or dtype=category
        in the columns_in_fit property. These columns will then be encoded
        by transform.
        """
        return self._detected_cols if self._is_fit else []

    def _detect_columns(self, X):

        # If cols is None, select all columns
        # with dtype = 'object', 'category'
        X_cat = X.select_dtypes(include=['object', 'category'])

        if self._columns is None or len(self._columns) == 0:
            self._detected_cols = []
            if not X_cat.empty:
                self._detected_cols = list(X_cat.columns)
        else:
            self._detected_cols = self._columns.copy()

        if self.encode_all_categoricals:
            not_in_cat_list = set(X_cat.columns) - set(self._detected_cols)
            self._detected_cols.extend(not_in_cat_list)

        # Remove columns that aren't in X
        safe_columns = [col for col in self._detected_cols
                        if col in X.columns]

        if set(safe_columns) != set(self._detected_cols):
            warn('Some columns were removed from the input '
                 + 'because they were not in the data frame. '
                 + 'final set')
            self._detected_cols = safe_columns

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X, y=None):
        """
        Fit the binarizer on the input data.

        :param X: Input data
        :type X: pandas.DataFrame
        :param y: Ignored. Necessary for pipeline compatibility

        :return: Fitted transform
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.CategoryBinarizer

        """
        # Rationalize self.columns with the input data frame
        self._detect_columns(X)

        # Save categorical levels
        self._categories_by_col = {col: pd.Categorical(X[col]).categories
                                   for col in self._detected_cols}

        self._is_fit = True
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X, y=None):
        """
        Transform requested columns via the encoder.

        :param X: Input data
        :type X: pandas.DataFrame
        :param y: Ignored. Necessary for pipeline compatibility

        :returns: Data with dummy coded categoricals
        :rtype: pandas.DataFrame

        """
        if not self._is_fit:
            raise UntrainedModelException.create_without_pii(
                target='CategoryBinarizer', reference_code='category_binarizer.CategoryBinarizer.transform')

        # If there are no categorical columns, this is just a pass-through
        if self._detected_cols is None or len(self._detected_cols) == 0:
            return X

        # Check that the categorical columns set at fit are still present
        missing_cols = set(self._detected_cols) - set(X.columns)
        if len(missing_cols) > 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfMissingColumn,
                                    target=TimeseriesDfMissingColumn.REGULAR_COLUMN,
                                    reference_code=ReferenceCodes._TST_NO_REGULAR_COLNAME,
                                    column_names=missing_cols)
            )

        # Check if X categoricals have categories not present at fit
        # If so, warn that they will be coded as NAs
        for col in self._detected_cols:
            now_cats = pd.Categorical(X[col]).categories
            fit_cats = self._categories_by_col[col]
            new_cats = set(now_cats) - set(fit_cats)
            if len(new_cats) > 0:
                warn('CategoryBinarizer.transform: Column contains '
                     + 'categories not present at fit. '
                     + 'These categories will be set to NA prior to encoding.')

        # Reassign X categorical columns so that they have the same set of
        #  categories as present at fit
        assign_dict = {
            col: pd.Categorical(X[col], categories=self._categories_by_col[col])
            for col in self._detected_cols
        }
        X_cat = X.assign(**assign_dict)

        # Do the dummy coding via pandas, suppress warning when
        # concatenating TimeSeriesDataFrame and pandas DataFrame
        with catch_warnings():
            simplefilter("ignore")
            X_dummies = pd.get_dummies(X_cat, prefix=self.prefix,
                                       prefix_sep=self.prefix_sep,
                                       dummy_na=self.dummy_na,
                                       columns=self._detected_cols,
                                       drop_first=self.drop_first,
                                       sparse=False)

        return X_dummies
