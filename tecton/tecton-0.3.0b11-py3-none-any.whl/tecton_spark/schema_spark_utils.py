from typing import Dict
from typing import Optional
from typing import Tuple

from pyspark.sql.types import ArrayType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DataType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructType
from pyspark.sql.types import TimestampType

from tecton_proto.common import column_type_pb2
from tecton_proto.common.schema_pb2 import Schema as SchemaProto
from tecton_spark.schema import Schema

# Keep in sync with SchemaUtils.kt
SPARK_TO_TECTON_TYPE = {
    "integer": column_type_pb2.COLUMN_TYPE_INT64,
    "long": column_type_pb2.COLUMN_TYPE_INT64,
    "float": column_type_pb2.COLUMN_TYPE_DOUBLE,
    "double": column_type_pb2.COLUMN_TYPE_DOUBLE,
    "string": column_type_pb2.COLUMN_TYPE_STRING,
    "boolean": column_type_pb2.COLUMN_TYPE_BOOL,
}

# Keep in sync with SchemaUtils.kt
SPARK_ARRAY_ELEMENT_TYPE_TO_TECTON_TYPES = {
    "long": ("long_array", column_type_pb2.COLUMN_TYPE_INT64_ARRAY),
    "float": ("float_array", column_type_pb2.COLUMN_TYPE_FLOAT_ARRAY),
    "double": ("double_array", column_type_pb2.COLUMN_TYPE_DOUBLE_ARRAY),
    "string": ("string_array", column_type_pb2.COLUMN_TYPE_STRING_ARRAY),
}

RAW_SPARK_TYPE_TO_SPARK_DATA_TYPE = {
    "timestamp": TimestampType(),
    "integer": IntegerType(),
    "long": LongType(),
    "float": FloatType(),
    "double": DoubleType(),
    "string": StringType(),
    "boolean": BooleanType(),
    "long_array": ArrayType(LongType()),
    "float_array": ArrayType(FloatType()),
    "double_array": ArrayType(DoubleType()),
    "string_array": ArrayType(StringType()),
}


def schema_from_spark(spark_schema: StructType) -> Schema:
    proto = SchemaProto()
    spark_dict = spark_schema.jsonValue()
    for field in spark_dict["fields"]:
        name = field["name"]
        column = proto.columns.add()
        column.name = name
        column_type, tecton_type = _tecton_type_from_spark_type(field["type"])

        if tecton_type:
            column.feature_server_type = tecton_type
        elif column_type == "timestamp":
            # Timestamp is an exception because it is required for the FV definition
            # but does not have a ColumnType because it's not written in materialized data.
            pass
        else:
            raise ValueError(f"Unsupported Spark type: '{column_type}' of column '{name}'")
        column.raw_spark_type = column_type
    return Schema(proto)


def _tecton_type_from_spark_type(spark_type: Dict) -> Tuple[str, Optional[int]]:
    if not isinstance(spark_type, dict):
        return spark_type, SPARK_TO_TECTON_TYPE.get(spark_type, None)

    if spark_type["type"] != "array":
        return spark_type, None

    return SPARK_ARRAY_ELEMENT_TYPE_TO_TECTON_TYPES.get(spark_type["elementType"], (spark_type, None))


def _spark_data_type_from_raw_spark_type(raw_spark_type: str) -> DataType:
    assert raw_spark_type in RAW_SPARK_TYPE_TO_SPARK_DATA_TYPE, "Unknown raw spark type: " + raw_spark_type
    return RAW_SPARK_TYPE_TO_SPARK_DATA_TYPE[raw_spark_type]


def schema_to_spark(schema: Schema) -> StructType:
    from pyspark.sql.types import StructType

    ret = StructType()
    for col_name, col_spark_data_type in column_name_spark_data_types(schema):
        ret.add(col_name, col_spark_data_type)
    return ret


def column_name_spark_data_types(schema: Schema):
    return [(c[0], _spark_data_type_from_raw_spark_type(c[1])) for c in schema.column_name_raw_spark_types()]
