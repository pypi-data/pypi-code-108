from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from common_client_scheduler.protobuf.generated.client_scheduler_messages_pb2 import (
    TransferConfigLocalProto,
    TransferConfigProto,
)
from terality_serde import SerdeMixin
from terality_serde.protobuf_wrapper import ProtobufWrapper


@dataclass
class TransferConfigLocal(ProtobufWrapper):
    _protobuf_class = TransferConfigLocalProto

    path: Path

    @property
    def proto(self) -> TransferConfigLocalProto:
        proto = TransferConfigLocalProto()
        proto.path = str(self.path)
        return proto

    @classmethod
    def from_proto(cls, proto: TransferConfigLocalProto) -> TransferConfigLocal:
        return TransferConfigLocal(
            path=Path(proto.path),
        )


@dataclass
class TransferConfig(ProtobufWrapper):
    _protobuf_class = TransferConfigProto

    default_aws_region: str
    bucket: str
    key_prefix: str

    @property
    def proto(self) -> TransferConfigProto:
        proto = TransferConfigProto()
        proto.default_aws_region = self.default_aws_region
        proto.bucket = self.bucket
        proto.key_prefix = self.key_prefix
        return proto

    @classmethod
    def from_proto(cls, proto: TransferConfigProto) -> TransferConfig:
        return TransferConfig(
            default_aws_region=proto.default_aws_region,
            bucket=proto.bucket,
            key_prefix=proto.key_prefix,
        )

    def bucket_region(self, aws_region: Optional[str] = None) -> str:
        """Return the name of the upload bucket in the given region."""
        return f"{self.bucket}-{self.default_aws_region if aws_region is None else aws_region}"


@dataclass
class SessionInfo(SerdeMixin):
    id: str  # pylint: disable=invalid-name
    upload_config: TransferConfig
    download_config: TransferConfig


@dataclass
class SessionInfoLocal(SerdeMixin):
    id: str  # pylint: disable=invalid-name
    upload_config: TransferConfigLocal
    download_config: TransferConfigLocal


SessionInfoType = Union[SessionInfo, SessionInfoLocal]
