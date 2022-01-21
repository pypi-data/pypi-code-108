from typing import Union

from common_client_scheduler import TransferConfig, TransferConfigLocal
from common_client_scheduler.protobuf.generated.client_scheduler_messages_pb2 import (
    OneOfTransferConfigProto,
)
from terality_serde.protobuf_helpers import ProtobufParser


class TransferConfigParser(ProtobufParser):
    protobuf_class = OneOfTransferConfigProto

    @classmethod
    def to_protobuf_message(
        cls, config: Union[TransferConfig, TransferConfigLocal]
    ) -> OneOfTransferConfigProto:
        proto = OneOfTransferConfigProto()
        if isinstance(config, TransferConfig):
            proto.transfer_config.MergeFrom(config.proto)
        if isinstance(config, TransferConfigLocal):
            proto.transfer_config_local.MergeFrom(config.proto)
        return proto

    @classmethod
    def to_terality_class(
        cls, proto: OneOfTransferConfigProto
    ) -> Union[TransferConfig, TransferConfigLocal]:
        config_type = proto.WhichOneof("config")

        if config_type == "transfer_config":
            return TransferConfig.from_proto(proto.transfer_config)
        if config_type == "transfer_config_local":
            return TransferConfigLocal.from_proto(proto.transfer_config_local)
        raise ValueError(f"Could not infer TransferConfig from proto={proto}")
