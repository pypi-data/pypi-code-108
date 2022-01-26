class ClientError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NonZeroExitCode(ClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidParameterError(ClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AccountDoesNotExistsError(NonZeroExitCode):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NetworkInterfaceNotExistsError(NonZeroExitCode):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ClientConnectionError(NonZeroExitCode):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlreadyConnectedError(ClientConnectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotConnectedError(ClientConnectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
