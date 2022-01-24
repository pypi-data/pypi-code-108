import grpc

from protos.data_consumer_pb2_grpc import DataConsumerStub
from protos.data_consumer_pb2 import ConsumerStopRequest
if __name__ == "__main__":
    with grpc.insecure_channel(f'[2a02:6b8:c02:900:0:f816:0:3ab]:17002') as channel:
        stub = DataConsumerStub(
            channel=channel
        )
        stub.Stop(ConsumerStopRequest())