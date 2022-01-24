class TaktileError(Exception):
    pass


class TaktileRuntimeError(TaktileError):
    pass


class TaktileSdkError(TaktileError):
    pass


class TaktileCliError(TaktileError):
    pass
