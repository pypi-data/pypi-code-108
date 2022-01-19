from typing import List

from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.args.entity_pb2 import EntityArgs
from tecton_spark.id_helper import IdHelper


def prepare_args(*, basic_info: BasicInfo, join_keys: List[str]) -> EntityArgs:
    args = EntityArgs()
    args.entity_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.info.CopyFrom(basic_info)
    args.join_keys.extend(join_keys)
    return args
