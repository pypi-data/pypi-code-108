from common_client_scheduler import (
    ComputationResponse,
    PendingComputationResponse,
    CreateSessionResponse,
    DeleteSessionResponse,
    DataTransferResponse,
    ImportFromCloudResponse,
    ExportToS3Response,
    ErrorResponse,
)
from common_client_scheduler.protobuf.generated.client_scheduler_messages_pb2 import (
    ProtobufServerResponseProto,
)
from common_client_scheduler.responses import (
    ProtobufResponse,
    CreateAnonymousUserResponse,
    ClientErrorContextResponse,
)
from common_client_scheduler.responses import ExportToAzureBlobStorageResponse, CreateUserResponse
from terality_serde.protobuf_helpers import ProtobufParser


class ProtobufResponseParser(ProtobufParser):
    protobuf_class = ProtobufServerResponseProto

    @classmethod
    def to_protobuf_message(cls, response: ProtobufResponse) -> ProtobufServerResponseProto:
        proto = ProtobufServerResponseProto()
        if isinstance(response, ComputationResponse):
            proto.computation_response.MergeFrom(response.proto)
        if isinstance(response, PendingComputationResponse):
            proto.pending_computation_response.MergeFrom(response.proto)
        if isinstance(response, CreateSessionResponse):
            proto.create_session_response.MergeFrom(response.proto)
        if isinstance(response, DeleteSessionResponse):
            proto.delete_session_response.MergeFrom(response.proto)
        if isinstance(response, DataTransferResponse):
            proto.data_transfer_response.MergeFrom(response.proto)
        if isinstance(response, ImportFromCloudResponse):
            proto.import_from_cloud_response.MergeFrom(response.proto)
        if isinstance(response, ExportToAzureBlobStorageResponse):
            proto.export_to_azure_response.MergeFrom(response.proto)
        if isinstance(response, ExportToS3Response):
            proto.export_to_s3_response.MergeFrom(response.proto)
        if isinstance(response, CreateUserResponse):
            proto.create_user_response.MergeFrom(response.proto)
        if isinstance(response, CreateAnonymousUserResponse):
            proto.create_anonymous_user_response.MergeFrom(response.proto)
        if isinstance(response, ErrorResponse):
            proto.error_response.MergeFrom(response.proto)
        if isinstance(response, ClientErrorContextResponse):
            proto.client_error_context_response.MergeFrom(response.proto)

        return proto

    @classmethod
    def to_terality_class(  # pylint: disable=too-many-return-statements
        cls, proto: ProtobufServerResponseProto
    ) -> ProtobufResponse:
        response_type = proto.WhichOneof("response")
        if response_type == "computation_response":
            return ComputationResponse.from_proto(proto.computation_response)
        if response_type == "pending_computation_response":
            return PendingComputationResponse.from_proto(proto.pending_computation_response)
        if response_type == "create_session_response":
            return CreateSessionResponse.from_proto(proto.create_session_response)
        if response_type == "delete_session_response":
            return DeleteSessionResponse.from_proto(proto.delete_session_response)
        if response_type == "data_transfer_response":
            return DataTransferResponse.from_proto(proto.data_transfer_response)
        if response_type == "import_from_cloud_response":
            return ImportFromCloudResponse.from_proto(proto.import_from_cloud_response)
        if response_type == "export_to_azure_response":
            return ExportToAzureBlobStorageResponse.from_proto(proto.export_to_azure_response)
        if response_type == "export_to_s3_response":
            return ExportToS3Response.from_proto(proto.export_to_s3_response)
        if response_type == "create_user_response":
            return CreateUserResponse.from_proto(proto.create_user_response)
        if response_type == "create_anonymous_user_response":
            return CreateAnonymousUserResponse.from_proto(proto.create_anonymous_user_response)
        if response_type == "error_response":
            return ErrorResponse.from_proto(proto.error_response)
        if response_type == "client_error_context_response":
            return ClientErrorContextResponse.from_proto(proto.client_error_context_response)

        raise ValueError(f"Could not infer response type from protobuf message {proto}")
