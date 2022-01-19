from typing import List

from google.protobuf import duration_pb2

from tecton_proto.common.schema_pb2 import Schema as SchemaProto
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion

CONTINUOUS_MODE_BATCH_INTERVAL = duration_pb2.Duration(seconds=86400)


def get_input_feature_columns(view_schema: SchemaProto, join_keys: List[str], timestamp_key: str) -> List[str]:
    column_names = (c.name for c in view_schema.columns)
    return [c for c in column_names if c not in join_keys and c != timestamp_key]


def validate_version(version):
    assert (
        version >= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT
        or version <= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_MAX
    )
