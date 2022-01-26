from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from common_client_scheduler.protobuf.generated.client_scheduler_messages_pb2 import (
    UploadProto,
    UploadRequestProto,
    ExportRequestProto,
    AwsPresignedUrlSourceProto,
    ObjectStorageKeyProto,
    ImportFromS3SourceProto,
    AzureBlobSourceProto,
    ImportFromAzureBlobStorageSourceProto,
    ImportFromCloudRequestProto,
    AwsS3ObjectPartExportRequestProto,
    AzureBlobStoragePartExportRequestProto,
    AwsS3PartsExportProto,
    AzureBlobStoragePartsExportProto,
    ExportToCloudRequestProto,
    CreateUserRequestProto,
    PandasFunctionRequestProto,
    FollowUpRequestProto,
    ClientErrorContextProto,
)
from terality_serde import SerializableEnum, dumps, loads
from terality_serde.protobuf_wrapper import ProtobufWrapper


@dataclass
class Upload(ProtobufWrapper):
    path: str

    @property
    def proto(self) -> UploadProto:
        proto = UploadProto()
        proto.path = self.path
        return proto

    @classmethod
    def from_proto(cls, proto: UploadProto) -> Upload:
        return Upload(
            path=proto.path,
        )


@dataclass
class UploadRequest(ProtobufWrapper):
    _protobuf_class = UploadRequestProto

    path: str
    transfer_id: str
    aws_region: Optional[str]

    @property
    def proto(self) -> UploadRequestProto:
        proto = UploadRequestProto()
        proto.path = self.path
        proto.transfer_id = self.transfer_id
        if self.aws_region is not None:
            proto.aws_region = self.aws_region
        return proto

    @classmethod
    def from_proto(cls, proto: UploadRequestProto) -> UploadRequest:
        return UploadRequest(
            path=proto.path,
            transfer_id=proto.transfer_id,
            aws_region=proto.aws_region if proto.HasField("aws_region") else None,
        )

    def terality_hash(self):
        return self.path


@dataclass
class ExportRequest(ProtobufWrapper):
    _protobuf_class = ExportRequestProto
    # Parameters of the "to_xxx" (to_csv, to_parquet...) function.
    # The server will echo it back in the response, but (as of now) don't use this information otherwise.
    path: str
    storage_options: Optional[Dict[str, Any]]
    # Preferred region for the Terality export bucket.
    aws_region: Optional[str]

    @property
    def proto(self) -> ExportRequestProto:
        proto = ExportRequestProto()
        proto.path = self.path
        if self.storage_options is not None:
            for option_key, option_value in self.storage_options.items():
                proto.storage_options[option_key] = option_value
        if self.aws_region is not None:
            proto.aws_region = self.aws_region
        return proto

    @classmethod
    def from_proto(cls, proto: ExportRequestProto) -> ExportRequest:
        return ExportRequest(
            path=proto.path,
            storage_options={
                key: value
                for key, value in proto.storage_options.items()  # pylint: disable=unnecessary-comprehension
            },
            aws_region=proto.aws_region if proto.HasField("aws_region") else None,
        )


class StorageService(SerializableEnum):
    AWS_S3 = "AWS_S3"
    AZURE_BLOB_STORAGE = "AZURE_BLOB_STORAGE"


@dataclass
class AwsPresignedUrlSource(ProtobufWrapper):
    """A presigned AWS URL allowing to run GetObject on an S3 object part."""

    _protobuf_class = AwsPresignedUrlSourceProto

    # Possible optimization: for the same object (bucket + key), the same presigned URL could
    # be reused for each range to get (the same presigned URL can be requested with different
    # Range HTTP headers).
    url: str
    object_key: ObjectStorageKey
    # warning, these offsets are inclusive
    range_start_byte: int
    range_end_byte: int

    @property
    def proto(self) -> AwsPresignedUrlSourceProto:
        proto = AwsPresignedUrlSourceProto()
        proto.url = self.url
        proto.object_key.MergeFrom(self.object_key.proto)
        proto.range_start_byte = self.range_start_byte
        proto.range_end_byte = self.range_end_byte
        return proto

    @classmethod
    def from_proto(cls, proto: AwsPresignedUrlSourceProto) -> AwsPresignedUrlSource:
        return AwsPresignedUrlSource(
            url=proto.url,
            object_key=ObjectStorageKey.from_proto(proto.object_key),
            range_start_byte=proto.range_start_byte,
            range_end_byte=proto.range_end_byte,
        )


@dataclass(frozen=True, order=True)
class ObjectStorageKey(ProtobufWrapper):
    """Generic representation of the path to an object (= blob in Azure) in some cloud storage service.

    (AWS Simple Storage Service (S3), Google Cloud Storage (GCS), Azure Blob Storage...)
    """

    _protobuf_class = ObjectStorageKeyProto

    bucket: str  # maps to a container in Azure Blob Storage, called "bucket" in most of the other services
    # (Azure Blob Storage also needs an extra "storage account name" information to uniquely identity
    # the blob. It should be transmitted along this object).

    key: str  # also called an "object name" in Google Cloud Storage and a "blob name" in Azure

    @property
    def proto(self) -> ObjectStorageKeyProto:
        proto = ObjectStorageKeyProto()
        proto.bucket = self.bucket
        proto.key = self.key
        return proto

    @classmethod
    def from_proto(cls, proto: ObjectStorageKeyProto) -> ObjectStorageKey:
        return ObjectStorageKey(
            bucket=proto.bucket,
            key=proto.key,
        )


@dataclass
class ImportFromS3Source(ProtobufWrapper):
    _protobuf_class = ImportFromS3SourceProto

    presigned_urls: List[AwsPresignedUrlSource]

    @property
    def proto(self) -> ImportFromS3SourceProto:
        proto = ImportFromS3SourceProto()
        proto.presigned_urls.extend([url.proto for url in self.presigned_urls])
        return proto

    @classmethod
    def from_proto(cls, proto: ImportFromS3SourceProto) -> ImportFromS3Source:
        return ImportFromS3Source(
            presigned_urls=[
                AwsPresignedUrlSource.from_proto(url_proto) for url_proto in proto.presigned_urls
            ]
        )


@dataclass
class AzureBlobSource(ProtobufWrapper):
    """A reference to an blob stored in Azure Blob storage, plus a shared access signature (SAS) that can read it.

    The SAS is a temporary credential generated by the Terality client that can be used as a credential
    to get read-only access to the given blob.
    """

    _protobuf_class = AzureBlobSourceProto

    object_key: ObjectStorageKey
    shared_access_signature: str
    storage_account_name: str
    # Possible optimization: for the same object (container + name), the same SAS could
    # be reused for each range to get.
    range_start_byte: int
    range_end_byte: int

    @property
    def proto(self) -> AzureBlobSourceProto:
        proto = AzureBlobSourceProto()
        proto.object_key.MergeFrom(self.object_key.proto)
        proto.shared_access_signature = self.shared_access_signature
        proto.storage_account_name = self.storage_account_name
        proto.range_start_byte = self.range_start_byte
        proto.range_end_byte = self.range_end_byte
        return proto

    @classmethod
    def from_proto(cls, proto: AzureBlobSourceProto) -> AzureBlobSource:
        return AzureBlobSource(
            object_key=ObjectStorageKey.from_proto(proto.object_key),
            shared_access_signature=proto.shared_access_signature,
            storage_account_name=proto.storage_account_name,
            range_start_byte=proto.range_start_byte,
            range_end_byte=proto.range_end_byte,
        )


# Even if the user provided an Azure Datalake Gen2 URL, the server always work
# at the Blob Storage level for import/exports. The client does the mapping.
@dataclass
class ImportFromAzureBlobStorageSource(ProtobufWrapper):
    _protobuf_class = ImportFromAzureBlobStorageSourceProto

    objects: List[AzureBlobSource]

    @property
    def proto(self) -> ImportFromAzureBlobStorageSourceProto:
        proto = ImportFromAzureBlobStorageSourceProto()
        proto.objects.extend([object_.proto for object_ in self.objects])
        return proto

    @classmethod
    def from_proto(
        cls, proto: ImportFromAzureBlobStorageSourceProto
    ) -> ImportFromAzureBlobStorageSource:
        return ImportFromAzureBlobStorageSource(
            objects=[AzureBlobSource.from_proto(object_proto) for object_proto in proto.objects]
        )


@dataclass
class ImportFromCloudRequest(ProtobufWrapper):
    _protobuf_class = ImportFromCloudRequestProto

    service: StorageService
    source: Union[ImportFromS3Source, ImportFromAzureBlobStorageSource]
    cache_disabled: bool = False

    @property
    def proto(self) -> ImportFromCloudRequestProto:
        proto = ImportFromCloudRequestProto()
        proto.service = dumps(self.service)
        if isinstance(self.source, ImportFromS3Source):
            proto.import_from_s3.MergeFrom(self.source.proto)
        if isinstance(self.source, ImportFromAzureBlobStorageSource):
            proto.import_from_azure.MergeFrom(self.source.proto)
        return proto

    @classmethod
    def from_proto(cls, proto: ImportFromCloudRequestProto) -> ImportFromCloudRequest:
        source_type = proto.WhichOneof("source")
        if source_type == "import_from_s3":
            return ImportFromCloudRequest(
                service=loads(proto.service),
                source=ImportFromS3Source.from_proto(proto.import_from_s3),
            )
        if source_type == "import_from_azure":
            return ImportFromCloudRequest(
                service=loads(proto.service),
                source=ImportFromAzureBlobStorageSource.from_proto(proto.import_from_azure),
            )
        raise ValueError(
            f"Could not infer type ImportFromS3Source | ImportFromAzureBlobStorageSource from proto={proto}"
        )


@dataclass
class AwsS3ObjectPartExportRequest(ProtobufWrapper):  # pylint: disable=too-many-instance-attributes
    """A presigned AWS URL allowing to run UploadPart on a S3 object part."""

    _protobuf_class = AwsS3ObjectPartExportRequestProto

    # Source
    source_object_key: ObjectStorageKey
    range_start_byte: int
    range_end_byte: int

    # Destination
    presigned_url: str

    # The server doesn't need to know the following pieces of information, but it makes writing the client
    # easier. Instead of matching the server results back using the URL (or an arbitrary ID), the server can
    # send back these IDs and the client can directly use them to complete the upload.
    # Note that the presigned URL already contains this in cleartext (we don't want want to rely on it,
    # but it shows that we don't have to consider this information as sensitive).
    multipart_upload_id: str
    part_number: int
    destination_object_key: ObjectStorageKey

    @property
    def proto(self) -> AwsS3ObjectPartExportRequestProto:
        proto = AwsS3ObjectPartExportRequestProto()
        proto.source_object_key.MergeFrom(self.source_object_key.proto)
        proto.range_start_byte = self.range_start_byte
        proto.range_end_byte = self.range_end_byte
        proto.presigned_url = self.presigned_url
        proto.multipart_upload_id = self.multipart_upload_id
        proto.part_number = self.part_number
        proto.destination_object_key.MergeFrom(self.destination_object_key.proto)
        return proto

    @classmethod
    def from_proto(cls, proto: AwsS3ObjectPartExportRequestProto) -> AwsS3ObjectPartExportRequest:
        return AwsS3ObjectPartExportRequest(
            source_object_key=ObjectStorageKey.from_proto(proto.source_object_key),
            range_start_byte=proto.range_start_byte,
            range_end_byte=proto.range_end_byte,
            presigned_url=proto.presigned_url,
            multipart_upload_id=proto.multipart_upload_id,
            part_number=proto.part_number,
            destination_object_key=ObjectStorageKey.from_proto(proto.destination_object_key),
        )


@dataclass
class AzureBlobStoragePartExportRequest(ProtobufWrapper):
    _protobuf_class = AzureBlobStoragePartExportRequestProto

    # Source
    source_object_key: ObjectStorageKey  # S3 object in the Terality export bucket
    range_start_byte: int
    range_end_byte: int

    # Destination
    destination_object_key: ObjectStorageKey  # (container, name) of an Azure Blob in storage_account_name
    storage_account_name: str
    shared_access_signature: str

    @property
    def proto(self) -> AzureBlobStoragePartExportRequestProto:
        proto = AzureBlobStoragePartExportRequestProto()
        proto.source_object_key.MergeFrom(self.source_object_key.proto)
        proto.range_start_byte = self.range_start_byte
        proto.range_end_byte = self.range_end_byte
        proto.destination_object_key.MergeFrom(self.destination_object_key.proto)
        proto.storage_account_name = self.storage_account_name
        proto.shared_access_signature = self.shared_access_signature
        return proto

    @classmethod
    def from_proto(
        cls, proto: AzureBlobStoragePartExportRequestProto
    ) -> AzureBlobStoragePartExportRequest:
        return AzureBlobStoragePartExportRequest(
            source_object_key=ObjectStorageKey.from_proto(proto.source_object_key),
            range_start_byte=proto.range_start_byte,
            range_end_byte=proto.range_end_byte,
            destination_object_key=ObjectStorageKey.from_proto(proto.destination_object_key),
            storage_account_name=proto.storage_account_name,
            shared_access_signature=proto.shared_access_signature,
        )


@dataclass
class AwsS3PartsExport(ProtobufWrapper):
    _protobuf_class = AwsS3PartsExportProto

    parts: List[AwsS3ObjectPartExportRequest]

    @property
    def proto(self) -> AwsS3PartsExportProto:
        proto = AwsS3PartsExportProto()
        proto.parts.extend([part.proto for part in self.parts])
        return proto

    @classmethod
    def from_proto(cls, proto: AwsS3PartsExportProto) -> AwsS3PartsExport:
        return AwsS3PartsExport(
            parts=[
                AwsS3ObjectPartExportRequest.from_proto(part_proto) for part_proto in proto.parts
            ]
        )


@dataclass
class AzureBlobStoragePartsExport(ProtobufWrapper):
    _protobuf_class = AzureBlobStoragePartsExportProto

    parts: List[AzureBlobStoragePartExportRequest]

    @property
    def proto(self) -> AzureBlobStoragePartsExportProto:
        proto = AzureBlobStoragePartsExportProto()
        proto.parts.extend([part.proto for part in self.parts])
        return proto

    @classmethod
    def from_proto(cls, proto: AzureBlobStoragePartsExportProto) -> AzureBlobStoragePartsExport:
        return AzureBlobStoragePartsExport(
            parts=[
                AzureBlobStoragePartExportRequest.from_proto(part_proto)
                for part_proto in proto.parts
            ]
        )


@dataclass
class ExportToCloudRequest(ProtobufWrapper):
    _protobuf_class = ExportToCloudRequestProto

    service: StorageService
    export_request: Union[AwsS3PartsExport, AzureBlobStoragePartsExport]

    @property
    def proto(self) -> ExportToCloudRequestProto:
        proto = ExportToCloudRequestProto()
        proto.service = dumps(self.service)

        if isinstance(self.export_request, AwsS3PartsExport):
            proto.s3_parts_export.MergeFrom(self.export_request.proto)
        if isinstance(self.export_request, AzureBlobStoragePartsExport):
            proto.azure_parts_export.MergeFrom(self.export_request.proto)

        return proto

    @classmethod
    def from_proto(cls, proto: ExportToCloudRequestProto) -> ExportToCloudRequest:
        request_type = proto.WhichOneof("export_request")
        if request_type == "s3_parts_export":
            return ExportToCloudRequest(
                service=loads(proto.service),
                export_request=AwsS3PartsExport.from_proto(proto.s3_parts_export),
            )
        if request_type == "azure_parts_export":
            return ExportToCloudRequest(
                service=loads(proto.service),
                export_request=AzureBlobStoragePartsExport.from_proto(proto.azure_parts_export),
            )
        raise ValueError(
            f"Could not infer type AwsS3PartsExport | AzureBlobStoragePartsExport from proto={proto}"
        )


@dataclass
class CreateUserRequest(ProtobufWrapper):
    _protobuf_class = CreateUserRequestProto

    email: str
    user_accepted_privacy_policy: bool
    user_accepted_terms_of_service: bool
    full_name: Optional[str]
    company: Optional[str]

    @property
    def proto(self) -> CreateUserRequestProto:
        proto = CreateUserRequestProto()
        proto.email = self.email
        proto.user_accepted_privacy_policy = self.user_accepted_privacy_policy
        proto.user_accepted_terms_of_service = self.user_accepted_terms_of_service
        if self.full_name is not None:
            proto.full_name = self.full_name
        if self.company is not None:
            proto.company = self.company
        return proto

    @classmethod
    def from_proto(cls, proto: CreateUserRequestProto) -> CreateUserRequest:
        return CreateUserRequest(
            email=proto.email,
            user_accepted_privacy_policy=proto.user_accepted_privacy_policy,
            user_accepted_terms_of_service=proto.user_accepted_terms_of_service,
            full_name=proto.full_name if proto.HasField("full_name") else None,
            company=proto.company if proto.HasField("company") else None,
        )


@dataclass
class PandasFunctionRequest(ProtobufWrapper):
    _protobuf_class = PandasFunctionRequestProto

    function_type: str
    function_accessor: Optional[str]
    function_name: str
    args: str
    kwargs: str
    cache_disabled: Optional[bool] = False

    @property
    def proto(self) -> PandasFunctionRequestProto:
        proto = PandasFunctionRequestProto()
        proto.function_type = self.function_type
        if self.function_accessor is not None:
            proto.function_accessor = self.function_accessor
        proto.function_name = self.function_name
        proto.args = self.args
        proto.kwargs = self.kwargs
        if self.cache_disabled is not None:
            proto.cache_disabled = self.cache_disabled
        return proto

    @classmethod
    def from_proto(cls, proto: PandasFunctionRequestProto) -> PandasFunctionRequest:
        return PandasFunctionRequest(
            function_type=proto.function_type,
            function_accessor=proto.function_accessor
            if proto.HasField("function_accessor")
            else None,
            function_name=proto.function_name,
            args=proto.args,
            kwargs=proto.kwargs,
            cache_disabled=proto.cache_disabled if proto.HasField("cache_disabled") else None,
        )

    @property
    def pretty_technical_name(self) -> str:
        """Return a readable but complete name for this function.

        Not intended to be understandable by an end user. Don't use this in error message
        or user-facing reporting.
        """
        accessor = f".{self.function_accessor}" if self.function_accessor else ""
        return f"{self.function_type}{accessor}.{self.function_name}"

    @property
    def external_name(self) -> str:
        user_friendly_function_type = (
            "" if self.function_type == "top_level" else f".{self.function_type}"
        )
        return f"te{user_friendly_function_type}.{self.function_name}"


@dataclass
class FollowUpRequest(ProtobufWrapper):
    _protobuf_class = FollowUpRequestProto

    function_id: str

    @property
    def proto(self) -> FollowUpRequestProto:
        proto = FollowUpRequestProto()
        proto.function_id = self.function_id
        return proto

    @classmethod
    def from_proto(cls, proto: FollowUpRequestProto) -> FollowUpRequest:
        return FollowUpRequest(
            function_id=proto.function_id,
        )


@dataclass
class ClientErrorContext(ProtobufWrapper):
    _protobuf_class = ClientErrorContextProto

    code: str
    filename: str
    exception_str: Optional[str]

    @property
    def proto(self) -> ClientErrorContextProto:
        proto = ClientErrorContextProto()
        proto.code = self.code
        proto.filename = self.filename
        if self.exception_str is not None:
            proto.exception_str = self.exception_str
        return proto

    @classmethod
    def from_proto(cls, proto: ClientErrorContextProto) -> ClientErrorContext:
        return ClientErrorContext(
            code=proto.code,
            filename=proto.filename,
            exception_str=proto.exception_str if proto.HasField("exception_str") else None,
        )


ProtobufRequest = Union[
    CreateUserRequest,
    ImportFromCloudRequest,
    ExportToCloudRequest,
    PandasFunctionRequest,
    FollowUpRequest,
    ClientErrorContext,
    ObjectStorageKey,
]
