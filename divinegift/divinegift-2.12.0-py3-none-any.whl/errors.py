class SenderNotInitializedError(Exception):
    pass


class KillException(Exception):
    pass


class ProducerNotSetError(Exception):
    pass


class ConsumerNotSetError(Exception):
    pass


class MethodNotAllowedError(Exception):
    pass


class EmptyConfigError(Exception):
    pass


class DBNotConnectedError(Exception):
    pass


class NoFileNamePassedError(Exception):
    pass
