from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field
from typing import Any, List, Union, Optional, Dict

from common_client_scheduler.config import TransferConfig, TransferConfigLocal
from common_client_scheduler.requests import ObjectStorageKey
from common_client_scheduler.helper import TransferConfigParser

from common_client_scheduler.protobuf.generated.client_scheduler_messages_pb2 import (
    PendingComputationResponseProto,
    ClientMessageProto,
    ComputationResponseProto,
    CreateSessionResponseProto,
    DeleteSessionResponseProto,
    ExportResponseProto,
    AwsCredentialsProto,
    DataTransferResponseProto,
    ImportFromCloudResponseProto,
    UploadedS3PartInfoProto,
    ExportToS3ResponseProto,
    ExportToAzureBlobStorageResponseProto,
    CreateUserResponseProto,
    ErrorResponseProto,
    CreateAnonymousUserResponseProto,
    ClientErrorContextResponseProto,
)
from terality_serde import dumps, loads
from terality_serde.protobuf_wrapper import ProtobufWrapper


@dataclass
class PendingComputationResponse(ProtobufWrapper):
    _protobuf_class = PendingComputationResponseProto
    pending_computation_id: str

    @property
    def proto(self) -> PendingComputationResponseProto:
        proto = PendingComputationResponseProto()
        proto.pending_computation_id = self.pending_computation_id
        return proto

    @classmethod
    def from_proto(cls, proto: PendingComputationResponseProto) -> PendingComputationResponse:
        return PendingComputationResponse(pending_computation_id=proto.pending_computation_id)


@dataclass
class ClientMessage(ProtobufWrapper):
    _protobuf_class = ClientMessageProto

    message: str
    log_level: int

    @property
    def proto(self) -> ClientMessageProto:
        proto = ClientMessageProto()
        proto.message = self.message
        proto.log_level = self.log_level
        return proto

    @classmethod
    def from_proto(cls, proto: ClientMessageProto) -> ClientMessage:
        return ClientMessage(message=proto.message, log_level=proto.log_level)


@dataclass
class ComputationResponse(ProtobufWrapper):
    _protobuf_class = ComputationResponseProto

    result: Any
    inplace: bool
    messages: List[ClientMessage] = field(default_factory=list)

    @property
    def proto(self) -> ComputationResponseProto:
        proto = ComputationResponseProto()
        proto.result = dumps(self.result)
        proto.inplace = self.inplace
        proto.messages.extend([message.proto for message in self.messages])
        return proto

    @classmethod
    def from_proto(cls, proto: ComputationResponseProto) -> ComputationResponse:
        return ComputationResponse(
            result=loads(proto.result),
            inplace=proto.inplace,
            messages=[ClientMessage.from_proto(message_proto) for message_proto in proto.messages],
        )


@dataclass
class CreateSessionResponse(ProtobufWrapper):
    _protobuf_class = CreateSessionResponseProto

    id: str  # pylint: disable=invalid-name
    download_config: Union[TransferConfig, TransferConfigLocal]
    upload_config: Union[TransferConfig, TransferConfigLocal]

    @property
    def proto(self) -> CreateSessionResponseProto:
        proto = CreateSessionResponseProto()
        proto.id = self.id
        proto.download_config.MergeFrom(
            TransferConfigParser.to_protobuf_message(self.download_config)
        )
        proto.upload_config.MergeFrom(TransferConfigParser.to_protobuf_message(self.upload_config))
        return proto

    @classmethod
    def from_proto(cls, proto: CreateSessionResponseProto) -> CreateSessionResponse:
        return CreateSessionResponse(
            id=proto.id,
            download_config=TransferConfigParser.to_terality_class(proto.download_config),
            upload_config=TransferConfigParser.to_terality_class(proto.upload_config),
        )


@dataclass
class DeleteSessionResponse(ProtobufWrapper):
    """Response to the delete session endpoint"""

    _protobuf_class = DeleteSessionResponseProto

    @property
    def proto(self) -> DeleteSessionResponseProto:
        return DeleteSessionResponseProto()

    @classmethod
    def from_proto(cls, _: DeleteSessionResponseProto) -> DeleteSessionResponse:
        return DeleteSessionResponse()


@dataclass
class ExportResponse(ProtobufWrapper):
    _protobuf_class = ExportResponseProto

    path: str
    storage_options: Optional[Dict[str, Any]]
    aws_region: Optional[str]
    transfer_id: str

    is_folder: bool  # True means it is the result of to_csv_folder or to_parquet_folder
    with_leading_zeros: bool = False  # Only relevant if is_folder is True. Output filename numbers will have leading zeros.

    @property
    def proto(self) -> ExportResponseProto:
        proto = ExportResponseProto()
        proto.path = self.path
        if self.storage_options is not None:
            for option_key, option_value in self.storage_options.items():
                proto.storage_options[option_key] = dumps(option_value)
        if self.aws_region is not None:
            proto.aws_region = self.aws_region
        proto.transfer_id = self.transfer_id
        proto.is_folder = self.is_folder
        proto.with_leading_zeros = self.with_leading_zeros
        return proto

    @classmethod
    def from_proto(cls, proto: ExportResponseProto) -> ExportResponse:
        return ExportResponse(
            path=proto.path,
            storage_options={
                key: loads(value)
                for key, value in proto.storage_options.items()  # pylint: disable=unnecessary-comprehension
            },
            aws_region=proto.aws_region if proto.HasField("aws_region") else None,
            transfer_id=proto.transfer_id,
            is_folder=proto.is_folder,
            with_leading_zeros=proto.with_leading_zeros,
        )


@dataclass
class AwsCredentials(ProtobufWrapper):
    _protobuf_class = AwsCredentialsProto

    access_key_id: str
    secret_access_key: str
    session_token: str

    @property
    def proto(self) -> AwsCredentialsProto:
        proto = AwsCredentialsProto()
        proto.access_key_id = self.access_key_id
        proto.secret_access_key = self.secret_access_key
        proto.session_token = self.session_token
        return proto

    @classmethod
    def from_proto(cls, proto: AwsCredentialsProto) -> AwsCredentials:
        return AwsCredentials(
            access_key_id=proto.access_key_id,
            secret_access_key=proto.secret_access_key,
            session_token=proto.session_token,
        )


@dataclass
class DataTransferResponse(ProtobufWrapper):
    _protobuf_class = DataTransferResponseProto
    temporary_upload_aws_credentials: AwsCredentials

    @property
    def proto(self) -> DataTransferResponseProto:
        proto = DataTransferResponseProto()
        proto.temporary_upload_aws_credentials.MergeFrom(
            self.temporary_upload_aws_credentials.proto
        )
        return proto

    @classmethod
    def from_proto(cls, proto: DataTransferResponseProto) -> DataTransferResponse:
        return DataTransferResponse(
            temporary_upload_aws_credentials=AwsCredentials.from_proto(
                proto.temporary_upload_aws_credentials
            ),
        )


@dataclass
class ImportFromCloudResponse(ProtobufWrapper):
    _protobuf_class = ImportFromCloudResponseProto

    transfer_id: str

    @property
    def proto(self) -> ImportFromCloudResponseProto:
        proto = ImportFromCloudResponseProto()
        proto.transfer_id = self.transfer_id
        return proto

    @classmethod
    def from_proto(cls, proto: ImportFromCloudResponseProto) -> ImportFromCloudResponse:
        return ImportFromCloudResponse(
            transfer_id=proto.transfer_id,
        )


@dataclass
class UploadedS3PartInfo(ProtobufWrapper):
    _protobuf_class = UploadedS3PartInfoProto

    destination_object_key: ObjectStorageKey
    etag: str
    part_number: int
    multipart_upload_id: str

    @property
    def proto(self) -> UploadedS3PartInfoProto:
        proto = UploadedS3PartInfoProto()
        proto.destination_object_key.MergeFrom(self.destination_object_key.proto)
        proto.etag = self.etag
        proto.part_number = self.part_number
        proto.multipart_upload_id = self.multipart_upload_id
        return proto

    @classmethod
    def from_proto(cls, proto: UploadedS3PartInfoProto) -> UploadedS3PartInfo:
        return UploadedS3PartInfo(
            destination_object_key=ObjectStorageKey.from_proto(proto.destination_object_key),
            etag=proto.etag,
            part_number=proto.part_number,
            multipart_upload_id=proto.multipart_upload_id,
        )


@dataclass
class ExportToS3Response(ProtobufWrapper):
    _protobuf_class = ExportToS3ResponseProto

    uploaded_parts: List[UploadedS3PartInfo]

    @property
    def proto(self) -> ExportToS3ResponseProto:
        proto = ExportToS3ResponseProto()
        proto.uploaded_parts.extend([part.proto for part in self.uploaded_parts])
        return proto

    @classmethod
    def from_proto(cls, proto: ExportToS3ResponseProto) -> ExportToS3Response:
        return ExportToS3Response(
            uploaded_parts=[
                UploadedS3PartInfo.from_proto(part_proto) for part_proto in proto.uploaded_parts
            ]
        )


@dataclass
class ExportToAzureBlobStorageResponse(ProtobufWrapper):
    _protobuf_class = ExportToAzureBlobStorageResponseProto

    @property
    def proto(self) -> ExportToAzureBlobStorageResponseProto:
        return ExportToAzureBlobStorageResponseProto()

    @classmethod
    def from_proto(
        cls, _: ExportToAzureBlobStorageResponseProto
    ) -> ExportToAzureBlobStorageResponse:
        return ExportToAzureBlobStorageResponse()


@dataclass
class CreateUserResponse(ProtobufWrapper):
    _protobuf_class = CreateUserResponseProto

    api_key: str

    @property
    def proto(self) -> CreateUserResponseProto:
        proto = CreateUserResponseProto()
        proto.api_key = self.api_key
        return proto

    @classmethod
    def from_proto(cls, proto: CreateUserResponseProto) -> CreateUserResponse:
        return CreateUserResponse(
            api_key=proto.api_key,
        )


@dataclass
class ErrorResponse(ProtobufWrapper):
    _protobuf_class = ErrorResponseProto

    message: str

    @property
    def proto(self) -> ErrorResponseProto:
        proto = ErrorResponseProto()
        proto.message = self.message
        return proto

    @classmethod
    def from_proto(cls, proto: ErrorResponseProto) -> ErrorResponse:
        return ErrorResponse(
            message=proto.message,
        )


@dataclass
class CreateAnonymousUserResponse(ProtobufWrapper):
    _protobuf_class = CreateAnonymousUserResponseProto

    user_id: str
    api_key: str
    expires_at: dt.datetime

    @property
    def proto(self) -> CreateAnonymousUserResponseProto:
        proto = CreateAnonymousUserResponseProto()
        proto.user_id = self.user_id
        proto.api_key = self.api_key
        proto.expires_at = dumps(self.expires_at)
        return proto

    @classmethod
    def from_proto(cls, proto: CreateAnonymousUserResponseProto) -> CreateAnonymousUserResponse:
        return CreateAnonymousUserResponse(
            user_id=proto.user_id,
            api_key=proto.api_key,
            expires_at=loads(proto.expires_at),
        )


@dataclass
class ClientErrorContextResponse(ProtobufWrapper):
    _protobuf_class = ClientErrorContextResponseProto

    status: str

    @property
    def proto(self) -> ClientErrorContextResponseProto:
        proto = ClientErrorContextResponseProto()
        proto.status = self.status
        return proto

    @classmethod
    def from_proto(cls, proto: ClientErrorContextResponseProto) -> ClientErrorContextResponse:
        return ClientErrorContextResponse(
            status=proto.status,
        )


ProtobufResponse = Union[
    ComputationResponse,
    PendingComputationResponse,
    CreateSessionResponse,
    DeleteSessionResponse,
    DataTransferResponse,
    ImportFromCloudResponse,
    ExportToAzureBlobStorageResponse,
    ExportToS3Response,
    CreateUserResponse,
    CreateAnonymousUserResponse,
    ErrorResponse,
    ClientErrorContextResponse,
]
