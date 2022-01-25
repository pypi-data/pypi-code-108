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
from pyspark.sql.types import TimestampType

from tecton_proto.common import column_type_pb2
from tecton_proto.common.schema_pb2 import Schema as SchemaProto
from tecton_spark.logger import get_logger

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

logger = get_logger("Schema")


class Schema:
    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def from_spark(cls, spark_schema):
        proto = SchemaProto()
        spark_dict = spark_schema.jsonValue()
        for field in spark_dict["fields"]:
            name = field["name"]
            column = proto.columns.add()
            column.name = name
            column_type, tecton_type = Schema._tecton_type_from_spark_type(field["type"])

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

    @staticmethod
    def _tecton_type_from_spark_type(spark_type) -> Tuple[str, Optional[int]]:
        if not isinstance(spark_type, dict):
            return spark_type, SPARK_TO_TECTON_TYPE.get(spark_type, None)

        if spark_type["type"] != "array":
            return spark_type, None

        return SPARK_ARRAY_ELEMENT_TYPE_TO_TECTON_TYPES.get(spark_type["elementType"], (spark_type, None))

    @staticmethod
    def _spark_data_type_from_raw_spark_type(raw_spark_type: str) -> DataType:
        assert raw_spark_type in RAW_SPARK_TYPE_TO_SPARK_DATA_TYPE, "Unknown raw spark type: " + raw_spark_type
        return RAW_SPARK_TYPE_TO_SPARK_DATA_TYPE[raw_spark_type]

    def to_spark(self):
        from pyspark.sql.types import StructType

        ret = StructType()
        for col_name, col_spark_data_type in self.column_name_spark_data_types():
            ret.add(col_name, col_spark_data_type)
        return ret

    def to_proto(self):
        return self._proto

    def tecton_type(self, column_name):
        c = self._column(column_name)
        return c.feature_server_type if c.HasField("feature_server_type") else None

    def spark_type(self, column_name):
        c = self._column(column_name)
        if not c.HasField("raw_spark_type"):
            raise ValueError(f"Column {column_name} is missing raw_spark_type")
        return c.raw_spark_type

    def _column(self, column_name):
        cs = [c for c in self._proto.columns if c.name == column_name]
        if not cs:
            raise ValueError(f"Unknown column: {column_name}. Schema is: {self._proto}")
        return cs[0]

    def column_names(self):
        return [c.name for c in self._proto.columns]

    def column_name_raw_spark_types(self):
        return [(c.name, c.raw_spark_type) for c in self._proto.columns]

    def column_name_spark_data_types(self):
        return [(c.name, Schema._spark_data_type_from_raw_spark_type(c.raw_spark_type)) for c in self._proto.columns]
