# Copyright 2019 Cognite AS

import inspect

import grpc


class CustomList(object):
    def __init__(self, get_stream):
        self.iterable = get_stream()
        self.get_stream = get_stream

    def __iter__(self):
        return iter(self.iterable)

    def to_list(self):
        self.load()
        return self.iterable

    def load(self):
        if not isinstance(self.iterable, list):
            retries = 5
            while True:
                try:
                    self.iterable = list(self.iterable)
                    break
                except grpc.RpcError as e:
                    if retries == 0 or e.code() != grpc.StatusCode.UNAVAILABLE:
                        break
                    self.iterable = self.get_stream()
                    retries -= 1
                    continue

    def to_map(self):
        trace_dict = dict()
        for trace in self.to_list():
            trace_dict[(trace.iline.value, trace.xline.value)] = trace.trace
        return trace_dict
