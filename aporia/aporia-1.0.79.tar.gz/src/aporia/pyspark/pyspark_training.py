from typing import Dict, List

import numpy as np
from pyspark.sql import DataFrame, functions

from aporia.core.consts import TRAINING_BIN_COUNT
from aporia.core.errors import AporiaError
from aporia.core.types.field import FieldType
from aporia.training.api.log_training import FieldTrainingData

MEDIAN_QUANTILE = 0.5


def calculate_dataframe_training_data(
    data: DataFrame, fields_schema: Dict[str, FieldType]
) -> List[FieldTrainingData]:
    """Calculates training data for a PySpark dataframe.

    Args:
        data: PySpark DataFrame.
        fields_schema: Fields schema for the category that is being calculated.

    Returns:
        Training data for all of the fields in the dataframe.
    """
    training_data = []
    for field_name in data.columns:
        # Ignore fields that are not defined in the model version schema
        if field_name not in fields_schema:
            continue

        training_data.append(
            calculate_pyspark_training_data(
                field_name=field_name,
                field_data=data.select(field_name),
                field_type=fields_schema[field_name],
            )
        )

    return training_data


def calculate_pyspark_training_data(
    field_name: str, field_data: DataFrame, field_type: FieldType
) -> FieldTrainingData:
    """Calculates training data for a single field in a PySpark DataFrame.

    Args:
        field_name: Field name
        field_data: Field data
        field_type: Field type

    Returns:
        Field training data.
    """
    # We currently don't support datetime, vector & text training data
    if field_type in [FieldType.DATETIME, FieldType.VECTOR, FieldType.TEXT]:
        return _calculate_training_data_without_histogram(
            field_name=field_name, field_data=field_data
        )
    elif field_type == FieldType.NUMERIC:
        return _calculate_numeric_training_data(field_name=field_name, field_data=field_data)
    elif field_type in [FieldType.BOOLEAN, FieldType.STRING, FieldType.CATEGORICAL]:
        return _calculate_categorical_training_data(
            field_name=field_name, field_data=field_data, field_type=field_type
        )

    raise AporiaError("Unsupported field type {} of field {}".format(field_type.value, field_name))


def _calculate_training_data_without_histogram(
    field_name: str, field_data: DataFrame
) -> FieldTrainingData:
    # Discard None and infinite values
    valid_values = field_data.replace([np.inf, np.NINF], None).dropna()

    field_data_count = field_data.count()
    valid_values_count = valid_values.count()

    return FieldTrainingData(
        field_name=field_name,
        num_samples=valid_values_count,
        num_missing_values=field_data_count - valid_values_count,
    )


def _calculate_categorical_training_data(
    field_name: str, field_data: DataFrame, field_type: FieldType
) -> FieldTrainingData:
    # Discard None and infinite values
    valid_values = field_data.replace([np.inf, np.NINF], None).dropna()
    if field_type == field_type.BOOLEAN:
        valid_values = valid_values.select(valid_values[field_name].cast("boolean"))

    distinct_values = valid_values.groupBy(field_name).count().orderBy(field_name)
    bins = []
    counts = []
    for row in distinct_values.collect():
        bins.append(row[field_name])
        counts.append(row["count"])

    field_data_count = field_data.count()
    valid_values_count = valid_values.count()

    return FieldTrainingData(
        field_name=field_name,
        bins=bins,
        counts=counts,
        num_samples=valid_values_count,
        num_missing_values=field_data_count - valid_values_count,
        num_unique_values=len(bins),
    )


def _calculate_numeric_training_data(field_name: str, field_data: DataFrame) -> FieldTrainingData:
    # Discard None and infinite values
    valid_values = field_data.replace([np.inf, np.NINF], None).dropna()

    # DataFrame.rdd returns an RDD (Resilient Distributed Dataset) of Rows, use a map
    # function to get an RDD of values.
    # More about RDDs: https://spark.apache.org/docs/latest/rdd-programming-guide.html
    valid_values_rdd = valid_values.rdd.map(lambda x: x[0])
    bins, counts = valid_values_rdd.histogram(TRAINING_BIN_COUNT)  # type: ignore

    median = valid_values.approxQuantile(
        col=field_name, probabilities=[MEDIAN_QUANTILE], relativeError=0
    )[0]

    field_data_aggs = field_data.agg(
        # For each of the following aggregations, we use a sum aggregation in conjunction with
        # a when-otherwise cluase that will return 1 if the condition is True and 0 otherwise
        functions.sum(
            functions.when(field_data[field_name].isin([None, np.nan]), 1).otherwise(0)
        ).alias("missing_values"),
        functions.sum(functions.when(field_data[field_name].isin([np.inf]), 1).otherwise(0)).alias(
            "posinf_values"
        ),
        functions.sum(functions.when(field_data[field_name].isin([np.NINF]), 1).otherwise(0)).alias(
            "neginf_values"
        ),
    ).collect()[0]

    valid_values_aggs = valid_values.agg(
        functions.max(field_name).alias("max"),
        functions.min(field_name).alias("min"),
        functions.sum(field_name).alias("sum"),
        functions.avg(field_name).alias("avg"),
        functions.stddev(field_name).alias("std"),
        functions.variance(field_name).alias("var"),
        # For each of the following aggregations, we use a sum aggregation in conjunction with
        # a when-otherwise cluase that will return 1 if the condition is True and 0 otherwise
        functions.sum(functions.when(valid_values[field_name] == 0, 1).otherwise(0)).alias(
            "zero_values"
        ),
    ).collect()[0]

    return FieldTrainingData(
        field_name=field_name,
        bins=bins,
        counts=counts,
        min=valid_values_aggs["min"],
        max=valid_values_aggs["max"],
        sum=valid_values_aggs["sum"],
        median=median,
        average=valid_values_aggs["avg"],
        std=valid_values_aggs["std"],
        variance=valid_values_aggs["var"],
        num_samples=valid_values.count(),
        num_missing_values=field_data_aggs["missing_values"],
        num_posinf_values=field_data_aggs["posinf_values"],
        num_neginf_values=field_data_aggs["neginf_values"],
        num_zero_values=valid_values_aggs["zero_values"],
    )
