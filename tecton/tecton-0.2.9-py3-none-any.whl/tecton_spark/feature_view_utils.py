from typing import List

from google.protobuf import duration_pb2
from pyspark.sql import DataFrame

from tecton_proto.common.schema_pb2 import Schema as SchemaProto
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_spark import errors
from tecton_spark.schema import Schema

CONTINUOUS_MODE_BATCH_INTERVAL = duration_pb2.Duration(seconds=86400)


def get_input_feature_columns(view_schema: SchemaProto, join_keys: List[str], timestamp_key: str) -> List[str]:
    column_names = (c.name for c in view_schema.columns)
    return [c for c in column_names if c not in join_keys and c != timestamp_key]


def validate_df_columns_and_feature_types(df: DataFrame, view_schema: Schema):
    df_columns = Schema.from_spark(df.schema).column_name_raw_spark_types()
    df_column_names = frozenset([x[0] for x in df_columns])
    fv_columns = view_schema.column_name_raw_spark_types()
    fv_column_names = frozenset([x[0] for x in fv_columns])

    if fv_column_names.difference(df_column_names):
        raise errors.INGEST_DF_MISSING_COLUMNS(list(fv_column_names.difference(df_column_names)))
    for fv_column in fv_columns:
        if fv_column not in df_columns:
            raise errors.INGEST_COLUMN_TYPE_MISMATCH(
                fv_column[0], fv_column[1], [x for x in df_columns if x[0] == fv_column[0]][0][1]
            )


def validate_version(version):
    assert (
        version >= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT
        or version <= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_MAX
    )
