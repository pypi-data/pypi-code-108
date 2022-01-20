# -*- coding: utf-8 -*-
class IncorrectRPCRequest(Exception):
    """
    This kind of exception occurs when there is an internal API error, possibly incorrect syntax of some function, or something else.
    """
    def __init__(self, msg):
        super(IncorrectRPCRequest, self).__init__(msg)


class RequestError(Exception):
    """
    Internal gRPC call error that occurs when the remote request processing has failed.
    """
    def __init__(self, msg):
        super(RequestError, self).__init__(msg)


class ComponentNotFound(Exception):
    """
    API error that occurs if the name of the declared variable is missing, mismatched, or unidentifiable
    """
    def __init__(self, msg):
        super(ComponentNotFound, self).__init__(msg)


class TimeoutError(Exception):
    """
    gRPC request timeout. See --timeout argument
    """
    def __init__(self, msg):
        super(TimeoutError, self).__init__(msg)


class ConnectError(Exception):
    """
    gRPC can't connect to Stub
    """
    def __init__(self, msg):
        super(ConnectError, self).__init__(msg)


class Exit(Exception):
    """
    A fatal exception that will trigger adapter instance to exit
    """
    pass
