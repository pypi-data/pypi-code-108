# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import math
from typing import Any, List, Optional, Union

import numpy as np
import pandas as pd
from forecast.data.sources.data_source import DataSourceConfig
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util

from ..constants import FeatureType, ForecastConstant, DROP_COLUMN_LIST, TCNForecastParameters
from ..types import DataInputType, TargetInputType
from .timeseries_datasets import _DataGrainItem, DNNTimeSeriesDatasetBase, TimeSeriesDataset


class TimeSeriesInferenceDataset(TimeSeriesDataset):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    def __init__(self,
                 X_dflow: DataInputType,
                 y_dflow: Optional[TargetInputType],
                 saved_data: pd.DataFrame,
                 horizon: int,
                 lookback: int,
                 dset_config: DataSourceConfig,
                 has_past_regressors: bool = False,
                 sample_transform: Any = None,
                 return_lookback: bool = True,
                 **settings: Any):
        """
        Take a inference data(X) and label(y) and provide the last item from each grain.

        :param X_dflow: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_dflow: Training label in DataPrep DataFlow for with shape(row_count, 1) or None.
        :param saved_data: Pandas Dataframe of last look back items from training data.
        :param horizon: Number of time steps to forecast.
        :param lookback: lookback for the model.
        :param dset_config: dataset settings
        :param has_past_regressors: data to populate past regressors for each sample
        :param sample_transform: feature transforms to use
        :param settings: automl timeseries settings
        """
        DNNTimeSeriesDatasetBase.__init__(self,
                                          horizon,
                                          lookback,
                                          step=1,
                                          has_past_regressors=has_past_regressors,
                                          sample_transform=sample_transform,
                                          fetch_y_only=False,
                                          dset_config=dset_config)

        self._return_lookback = return_lookback
        X_df, y_df = _wrapper_util.convert_X_y_to_pandas(X_dflow, y_dflow)
        if y_df is None:
            y_df = pd.DataFrame([np.nan] * X_df.shape[0])

        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        X_df[target_column] = y_df.values

        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
            grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        self._time_column = settings[ForecastConstant.time_column_name]

        # If no grains, drop any dummy grain column. Keep the time column as the only index
        if grains is None:
            X_df.index = X_df.index.get_level_values(self._time_column)

        self._index_columns = X_df.index.names
        X_df.reset_index(inplace=True)
        saved_indexed = saved_data.reset_index()  # We are copying input dat.
        saved_indexed.set_index(self._time_column, inplace=True)

        saved_df_list = []
        if grains is None:
            if X_df.shape[0] < self.lookback + self.horizon:
                min_time_value = min(X_df[self._time_column])
                saved = saved_indexed[saved_indexed.index < min_time_value]
                saved.reset_index(inplace=True)
                saved_df_list.append(saved[X_df.columns])
            self._len = 1
        else:
            Xdf_indexed = X_df.set_index(self._time_column)
            Xdf_indexed.sort_index(axis=0, inplace=True)
            Xdf_grains = Xdf_indexed.groupby(grains)
            saved_grains = saved_indexed.groupby(grains)
            grain_keys = Xdf_grains.groups.keys()
            saved_keys = saved_grains.groups.keys()
            self._len = 0
            for grain_key in grain_keys:
                self._len += 1
                grain_item = Xdf_grains.get_group(grain_key)
                if grain_key in saved_keys:
                    if grain_item.shape[0] < self.lookback + self.horizon:
                        saved_item = saved_grains.get_group(grain_key)
                        min_time_value = min(grain_item.index)
                        saved = saved_item[saved_item.index < min_time_value]
                        saved.reset_index(inplace=True)
                        saved_df_list.append(saved[X_df.columns])

        if(len(saved_df_list) > 0):
            X_df = pd.concat([X_df] + saved_df_list, axis=0)

        X_df.set_index(self._index_columns, inplace=True)
        X_df.sort_index(inplace=True)
        y_df = X_df.pop(target_column)
        self._drop_extra_columns(X_df, inplace=True)

        # A list of every grain in the timeseries.
        # It is expected that grains are sorted in ascending order by time-column.
        self._data_grains: List[_DataGrainItem] = []

        X_df.insert(0, target_column, y_df.values)

        count_per_grain_needed = self.lookback + self.horizon
        offset = 0

        if grains is None:
            # set the index to last item.
            self._append_grain_item(X_df, y_df, count_per_grain_needed, offset)
        else:
            offset = 0
            groupby_X_df = X_df.groupby(grains)
            for _, grain_df in groupby_X_df:
                self._append_grain_item(grain_df, grain_df[target_column], count_per_grain_needed, offset)
                offset += 1

    def _append_grain_item(self, X_df: pd.DataFrame, y_df: pd.DataFrame, count_per_grain_needed: int, offset: int):
        """
        Add a slice from the incoming dataframes to a DataGrainItem.

        :param X_df: Training features ).
        :param y_df: Training label
        :param count_per_grain_needed: Number of items needed to inference a horizon.
        :param offset: offset for the new data iten with in the Dataset, one item per grain.
        """
        X_item = X_df.iloc[-(count_per_grain_needed):]
        y_item = y_df.iloc[-(count_per_grain_needed):]
        self._data_grains.append(_DataGrainItem(X_item,
                                                y_item.values.reshape(1, y_item.shape[0]),
                                                offset,
                                                offset + 1,
                                                0))
