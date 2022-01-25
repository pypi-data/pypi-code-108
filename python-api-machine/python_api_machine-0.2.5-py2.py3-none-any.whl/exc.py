from dataclasses import dataclass


@dataclass
class ErrorPayload:
    result_type: str
    error_type: str
    msg: str


class ClientError(RuntimeError):
    @property
    def msg(self):
        if hasattr(self, "__msg__"):
            return self.__msg__.format(self=self)

    @property
    def payload(self):
        return ErrorPayload(**{
            "result_type": "error",
            "error_type": self.__class__.__name__,
            "msg": self.msg,
        })


@dataclass
class ObjectNotFound(ClientError):
    table: str
    key: dict
    __msg__ = "Object in {self.table} with {self.key} does not exist"


class InvalidMessage(ClientError):
    pass


@dataclass
class ValidationError(ClientError):
    detail: str

    @property
    def msg(self):
        return self.detail


class OperationDoesNotExist(InvalidMessage):
    pass
