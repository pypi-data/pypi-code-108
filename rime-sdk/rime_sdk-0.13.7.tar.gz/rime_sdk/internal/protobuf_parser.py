"""Library for converting Protobufs to Python data types such as dataframes."""

from typing import Dict, Optional

import pandas as pd
from google.protobuf.json_format import MessageToDict

from rime_sdk.protos.test_run_results.test_run_results_pb2 import TestRun

# Map of flattened field paths to their types in the Dataframe.
default_test_run_column_info = {
    # Metadata.
    "metadata.id": "str",
    "metadata.name": "str",
    "metadata.project_id": "str",
    "metadata.model_task": "str",  # OPTIONAL
    "metadata.upload_time": "str",
    # Model source info.
    "model_source_info.name": "str",  # OPTIONAL
    # Data source info.
    "data_source_info.ref.name": "str",
    "data_source_info.eval.name": "str",
    # Metrics.
    "metrics.duration_millis": "float",
    "metrics.num_inputs": "Int64",
    "metrics.num_failing_inputs": "Int64",
    "metrics.summary_counts.total": "Int64",
    "metrics.summary_counts.pass": "Int64",
    "metrics.summary_counts.warning": "Int64",
    "metrics.summary_counts.fail": "Int64",
    "metrics.severity_counts.none": "Int64",
    "metrics.severity_counts.low": "Int64",
    "metrics.severity_counts.medium": "Int64",
    "metrics.severity_counts.high": "Int64",
}

# Separator to use when flattening JSON into a dataframe.
# columns_to_keep definition relies on this separator.
df_flatten_separator = "."


def parse_test_run_metadata(
    test_run: TestRun, version: Optional[str] = None,  # pylint: disable=W0613
) -> pd.DataFrame:
    """Parse test run metadata Protobuf message into a Pandas dataframe.

    The columns are not guaranteed to be returned in sorted order.
    Some values are optional and will appear as a NaN value in the dataframe.

    Results can be fixed to a version by providing the keyword argument `version`.
    """
    # Use the canonical JSON encoding for Protobuf messages.
    test_run_dict = MessageToDict(
        test_run,
        # including_default_value_fields only operates at the highest level of nesting -
        # it does not traverse subtrees of nested messages.
        # For example, if metrics.summary_counts is None, then none of its value will be
        # filled in with zeros.
        including_default_value_fields=True,
        # This ensures that the field names will be snake_case.
        preserving_proto_field_name=True,
    )

    default_test_run_columns = list(default_test_run_column_info.keys())
    # Flatten out nested fields in the Protobuf message.
    # The DF column name will be the field path joined by the `df_flatten_separator.`
    normalized_df = pd.json_normalize(test_run_dict, sep=df_flatten_separator)
    missing_columns = set(default_test_run_columns).difference(
        set(normalized_df.columns)
    )
    intersect_df = normalized_df[
        normalized_df.columns.intersection(default_test_run_columns)
    ]

    # Fill in the missing columns with None values.
    kwargs: Dict[str, None] = {}
    for column in missing_columns:
        kwargs[column] = None
    # Note that this step does not preserve column order.
    full_df = intersect_df.assign(**kwargs)

    # The canonical Protobuf<>JSON encoding converts int64 values to string,
    # so we need to convert them back.
    # https://developers.google.com/protocol-buffers/docs/proto3#json
    for key, value in default_test_run_column_info.items():
        if value == "Int64":
            # Some nested fields such as `metrics.severity_counts.low` will be `None`
            # because MessageToDict does not populate nested primitive fields with
            # default values.
            # Since some columns may be `None`, we must convert to `float` first.
            # https://stackoverflow.com/questions/60024262/error-converting-object-string-to-int32-typeerror-object-cannot-be-converted  # pylint: disable=line-too-long
            full_df[key] = full_df[key].astype("float").astype("Int64")

    # We omit the extra step of sorting the columns because Pandas reindexing changes
    # the data types of columns.
    # This is fine because the dataframe access pattern will likely involve column
    # names more than integer indices.
    return full_df
