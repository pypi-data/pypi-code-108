class CpywpaError(Exception):
    pass


class ParametersError(CpywpaError):
    pass


class AddNetworkError(CpywpaError):
    pass


class EnableNetworkError(CpywpaError):
    pass


class ConnectError(CpywpaError):
    pass


class BusyError(CpywpaError):
    pass


class RemoveError(CpywpaError):
    pass
