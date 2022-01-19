from typing import Dict
from typing import List
from typing import Union

from pyspark.sql.types import ArrayType
from pyspark.sql.types import AtomicType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructType

from tecton_proto.args.pipeline_pb2 import RequestContext as RequestContextProto
from tecton_proto.data.new_transformation_pb2 import NewTransformation as TransformationDataProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_spark import errors
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

InputType = Union["VirtualDataSourceProto", "TransformationDataProto"]
TRANSFORMATION_TEMP_VIEW_PREFIX = "_tecton_transformation_"

VALID_FEATURE_SERVER_TYPES = [
    LongType(),
    DoubleType(),
    StringType(),
    BooleanType(),
    ArrayType(LongType()),
    ArrayType(FloatType()),
    ArrayType(DoubleType()),
    ArrayType(StringType()),
]
VALID_FEATURE_SERVER_TYPES_ERROR_STR = ", ".join([str(t) for t in VALID_FEATURE_SERVER_TYPES])


class _RequestContext:
    """
    Wrapper around the RequestContext proto object (that is part of the RequestDataSourceNode in the FV pipeline).
    """

    def __init__(self, schema: Dict[str, AtomicType]):
        """
        Creates a _RequestContext object.

        :param schema: Dictionary mapping string -> data types. Supported types are LongType, DoubleType, StringType, BooleanType.
        """
        for field, typ in schema.items():
            if typ not in VALID_FEATURE_SERVER_TYPES:
                raise errors.TectonValidationError(
                    f"RequestContext schema type {typ} for field '{field}' not supported. Expected one of {VALID_FEATURE_SERVER_TYPES_ERROR_STR}"
                )

        self.arg_to_schema = schema

    def _to_proto(self) -> RequestContextProto:
        s = StructType()
        for field, typ in self.arg_to_schema.items():
            s.add(field, typ)
        wrapper = SparkSchemaWrapper(s)
        return RequestContextProto(schema=wrapper.to_proto())

    def _set_schema_field_order(self, schema_field_order: List[str]):
        """
        Forces an ordering for schemas with multiple fields.

        :param schema_field_order: Ordered list of schema fields.
        """
        assert set(schema_field_order) == set(self.arg_to_schema.keys()) and len(schema_field_order) == len(
            self.arg_to_schema.keys()
        ), f"Schema ordering fields {schema_field_order} must contain the same elements as schema dictionary keys {list(self.arg_to_schema.keys())}."
        new_schema = {}
        for field in schema_field_order:
            new_schema[field] = self.arg_to_schema[field]
        self.arg_to_schema = new_schema

    @classmethod
    def _from_proto(cls, proto: RequestContextProto):
        wrapper = SparkSchemaWrapper.from_proto(proto.schema)
        schema_dict = {field: typ for field, typ in wrapper.column_name_types()}
        return _RequestContext(schema=schema_dict)

    def _merge(self, other):
        for field in other.arg_to_schema:
            if field in self.arg_to_schema:
                # should not happen
                assert (
                    self.arg_to_schema[field] == other.arg_to_schema[field]
                ), f"Mismatched request context field types for {field}"
            else:
                self.arg_to_schema[field] = other.arg_to_schema[field]
