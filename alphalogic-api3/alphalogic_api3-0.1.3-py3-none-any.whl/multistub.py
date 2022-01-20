# -*- coding: utf-8 -*-
import grpc
from alphalogic_api3.logger import log
from alphalogic_api3.exceptions import IncorrectRPCRequest, RequestError, ComponentNotFound, TimeoutError, ConnectError
from alphalogic_api3 import options

from alphalogic_api3.protocol.rpc_pb2 import (
    ObjectRequest,
    ParameterRequest,
    EventRequest,
    CommandRequest,
    StateStream
)

from alphalogic_api3.protocol.rpc_pb2_grpc import (
    ObjectServiceStub,
    ParameterServiceStub,
    EventServiceStub,
    CommandServiceStub,
    StateServiceStub,
    ObjectServiceServicer,
    ParameterServiceServicer,
    EventServiceServicer,
    CommandServiceServicer,
    StateServiceServicer
)


class MultiStub(object):

    def __init__(self, target):
        self.channel = grpc.insecure_channel(target)
        self.stub_object = ObjectServiceStub(self.channel)
        self.stub_parameter = ParameterServiceStub(self.channel)
        self.stub_event = EventServiceStub(self.channel)
        self.stub_command = CommandServiceStub(self.channel)
        self.stub_service = StateServiceStub(self.channel)

    @staticmethod
    def static_initialization():
        MultiStub.object_fun_set = MultiStub.dict_create_helper(ObjectServiceServicer)
        MultiStub.parameter_fun_set = MultiStub.dict_create_helper(ParameterServiceServicer)
        MultiStub.event_fun_set = MultiStub.dict_create_helper(EventServiceServicer)
        MultiStub.command_fun_set = MultiStub.dict_create_helper(CommandServiceServicer)
        MultiStub.service_fun_set = MultiStub.dict_create_helper(StateServiceServicer)

    @staticmethod
    def dict_create_helper(service):
        """
        Get Service methods excluded _
        """
        is_callable = lambda x: callable(getattr(service, x)) and not x.startswith('_')
        return set(list(filter(is_callable, dir(service))))

    def object_call(self, *args, **kwargs):
        obj_w = ObjectRequest(**kwargs)
        return self.call_helper(*args, fun_set=MultiStub.object_fun_set,  request=obj_w, stub=self.stub_object)

    def parameter_call(self, *args, **kwargs):
        par_w = ParameterRequest(**kwargs)
        return self.call_helper(*args, fun_set=MultiStub.parameter_fun_set, request=par_w, stub=self.stub_parameter)

    def event_call(self, *args, **kwargs):
        event_w = EventRequest(**kwargs)
        return self.call_helper(*args, fun_set=MultiStub.event_fun_set, request=event_w, stub=self.stub_event)

    def command_call(self, *args, **kwargs):
        command_w = CommandRequest(**kwargs)
        return self.call_helper(*args, fun_set=MultiStub.command_fun_set, request=command_w, stub=self.stub_command)

    def state_call(self, *args, **kwargs):
        state_w = StateStream(**kwargs)
        return self.call_helper(*args, fun_set=MultiStub.service_fun_set, request=state_w, stub=self.stub_service)

    def call_helper(self, function_name, *args, **kwargs):
        if function_name in kwargs['fun_set']:  # function_name - check availability
            try:
                answer = getattr(kwargs['stub'], function_name)(kwargs['request'], timeout=options.args.timeout)
                return answer

            except grpc.RpcError as err:
                if err.code() == grpc.StatusCode.NOT_FOUND:
                    raise ComponentNotFound(err.details())
                elif err.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise TimeoutError(err.details())
                elif err.code() == grpc.StatusCode.UNAVAILABLE:
                    raise ConnectError(err.details())
                raise RequestError(f'gRPC request failed (code={err.code()}): {err.details()}')
        else:
            raise IncorrectRPCRequest(f'{function_name} not found in {kwargs["fun_set"]}')


log.info("static MultiStub initialization")
MultiStub.static_initialization()
