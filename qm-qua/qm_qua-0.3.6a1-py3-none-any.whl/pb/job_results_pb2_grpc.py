# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from qm.pb import job_results_pb2 as qm_dot_pb_dot_job__results__pb2


class JobResultsServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetJobResultSchema = channel.unary_unary(
                '/qm.grpc.results_analyser.JobResultsService/GetJobResultSchema',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaResponse.FromString,
                )
        self.GetJobState = channel.unary_unary(
                '/qm.grpc.results_analyser.JobResultsService/GetJobState',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobStateRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobStateResponse.FromString,
                )
        self.GetJobNamedResultHeader = channel.unary_unary(
                '/qm.grpc.results_analyser.JobResultsService/GetJobNamedResultHeader',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderResponse.FromString,
                )
        self.GetJobNamedResult = channel.unary_stream(
                '/qm.grpc.results_analyser.JobResultsService/GetJobNamedResult',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultResponse.FromString,
                )
        self.GetJobDebugData = channel.unary_stream(
                '/qm.grpc.results_analyser.JobResultsService/GetJobDebugData',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobDebugDataRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobDebugDataResponse.FromString,
                )
        self.GetJobErrors = channel.unary_unary(
                '/qm.grpc.results_analyser.JobResultsService/GetJobErrors',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetJobErrorsRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobErrorsResponse.FromString,
                )
        self.GetProgramMetadata = channel.unary_unary(
                '/qm.grpc.results_analyser.JobResultsService/GetProgramMetadata',
                request_serializer=qm_dot_pb_dot_job__results__pb2.GetProgramMetadataRequest.SerializeToString,
                response_deserializer=qm_dot_pb_dot_job__results__pb2.GetProgramMetadataResponse.FromString,
                )


class JobResultsServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetJobResultSchema(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobNamedResultHeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobNamedResult(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobDebugData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobErrors(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetProgramMetadata(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_JobResultsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetJobResultSchema': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobResultSchema,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaResponse.SerializeToString,
            ),
            'GetJobState': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobState,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobStateRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobStateResponse.SerializeToString,
            ),
            'GetJobNamedResultHeader': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobNamedResultHeader,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderResponse.SerializeToString,
            ),
            'GetJobNamedResult': grpc.unary_stream_rpc_method_handler(
                    servicer.GetJobNamedResult,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobNamedResultResponse.SerializeToString,
            ),
            'GetJobDebugData': grpc.unary_stream_rpc_method_handler(
                    servicer.GetJobDebugData,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobDebugDataRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobDebugDataResponse.SerializeToString,
            ),
            'GetJobErrors': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobErrors,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetJobErrorsRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetJobErrorsResponse.SerializeToString,
            ),
            'GetProgramMetadata': grpc.unary_unary_rpc_method_handler(
                    servicer.GetProgramMetadata,
                    request_deserializer=qm_dot_pb_dot_job__results__pb2.GetProgramMetadataRequest.FromString,
                    response_serializer=qm_dot_pb_dot_job__results__pb2.GetProgramMetadataResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'qm.grpc.results_analyser.JobResultsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class JobResultsService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetJobResultSchema(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobResultSchema',
            qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobResultSchemaResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobState',
            qm_dot_pb_dot_job__results__pb2.GetJobStateRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobStateResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobNamedResultHeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobNamedResultHeader',
            qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobNamedResultHeaderResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobNamedResult(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobNamedResult',
            qm_dot_pb_dot_job__results__pb2.GetJobNamedResultRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobNamedResultResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobDebugData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobDebugData',
            qm_dot_pb_dot_job__results__pb2.GetJobDebugDataRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobDebugDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobErrors(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qm.grpc.results_analyser.JobResultsService/GetJobErrors',
            qm_dot_pb_dot_job__results__pb2.GetJobErrorsRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetJobErrorsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetProgramMetadata(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qm.grpc.results_analyser.JobResultsService/GetProgramMetadata',
            qm_dot_pb_dot_job__results__pb2.GetProgramMetadataRequest.SerializeToString,
            qm_dot_pb_dot_job__results__pb2.GetProgramMetadataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
