from pyspark.sql import DataFrame

from tecton_spark import errors
from tecton_spark.schema import Schema
from tecton_spark.schema_spark_utils import schema_from_spark


def validate_df_columns_and_feature_types(df: DataFrame, view_schema: Schema):
    df_columns = schema_from_spark(df.schema).column_name_raw_spark_types()
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
