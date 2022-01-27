class ConnectionClosedException(Exception):
    pass


class RetriesExceededException(Exception):
    pass


class NoRouteFoundException(Exception):
    pass


class NoConsumerException(Exception):
    pass


class UnknownBodyTypeException(Exception):
    pass


class CorruptedBodyException(Exception):
    pass
