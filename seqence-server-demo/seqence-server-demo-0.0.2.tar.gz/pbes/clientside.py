#!/usr/bin/env python3

from pydoc import cli
import grpc
import logging


from pbes import sequense_pb2
from pbes import sequense_pb2_grpc


def client():
    with grpc.insecure_channel("127.0.0.1:10352") as channel:
        stub = sequense_pb2_grpc.SequenceServerStub(channel)
        response = stub.get(sequense_pb2.SequenceRequest())
        print(response.sequence)
