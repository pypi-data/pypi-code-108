# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Tuple

import azureml.dataprep as dprep
from azureml.automl.core.constants import FeatureType
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector


class DataCharacteristics:
    """Data class to capture characteristics of interest."""

    def __init__(
            self,
            num_rows: float,
            num_numerical_columns: int,
            num_categorical_columns: int,
            num_text_columns: int
    ) -> None:
        self.num_rows = int(num_rows)  # type: int
        self.num_numerical_columns = num_numerical_columns  # type: int
        self.num_categorical_columns = num_categorical_columns  # type: int
        self.num_text_columns = num_text_columns  # type: int


class DataCharacteristicsCalculator:
    """A tool to produce data characteristics"""

    ROW_COUNT_FOR_COLUMN_PURPOSE = 10000

    @staticmethod
    def calc_data_characteristics(dataflow: dprep.Dataflow) -> DataCharacteristics:
        """Calculate data characteristics for a Dataflow."""
        num_numeric, num_categorical, num_text = DataCharacteristicsCalculator._get_column_type_count(dataflow)
        row_count = DataCharacteristicsCalculator._get_row_count(dataflow)
        return DataCharacteristics(
            num_rows=row_count,
            num_numerical_columns=num_numeric,
            num_categorical_columns=num_categorical,
            num_text_columns=num_text)

    @staticmethod
    def _get_column_type_count(dataflow: dprep.Dataflow) -> Tuple[int, int, int]:
        num_numeric = 0
        num_categorical = 0
        num_text = 0
        data_for_stats = dataflow.take(
            DataCharacteristicsCalculator.ROW_COUNT_FOR_COLUMN_PURPOSE).to_pandas_dataframe()
        stats_and_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(data_for_stats)
        for _, column_purpose, column in stats_and_purposes:
            if column_purpose == FeatureType.Numeric:
                num_numeric = num_numeric + 1
            elif column_purpose == FeatureType.Categorical or column_purpose == FeatureType.CategoricalHash \
                    or column_purpose == FeatureType.DateTime:
                num_categorical = num_categorical + 1
            elif column_purpose == FeatureType.Text:
                num_text = num_text + 1

        return num_numeric, num_categorical, num_text

    @staticmethod
    def _get_row_count(dataflow: dprep.Dataflow) -> int:
        """Get the number of rows in the raw training data."""
        # Here, we calculate the profile for the first column of the Dataflow. This enables us to
        # count # of rows while avoiding the unnecessary speed slowdown of calculating the profile stats
        # for the whole Dataflow.
        columns = dataflow.take(1).get_profile().columns
        if not len(columns):
            return 0

        first_column_profile = dataflow.keep_columns([next(iter(columns))]).get_profile()
        ret = first_column_profile.row_count  # type: int
        return ret
