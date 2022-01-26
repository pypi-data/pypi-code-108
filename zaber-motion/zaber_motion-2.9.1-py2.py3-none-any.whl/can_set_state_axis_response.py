# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from .protobufs import main_pb2


class CanSetStateAxisResponse:
    """
    An object containing any setup issues that will prevent setting a state to a given peripheral.
    """

    @property
    def error(self) -> str:
        """
        The error blocking applying this state to the given axis.
        """

        return self._error

    @error.setter
    def error(self, value: str) -> None:
        self._error = value

    @property
    def axis_number(self) -> int:
        """
        The number of the axis that cannot be set.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.CanSetStateAxisResponse
    ) -> 'CanSetStateAxisResponse':
        instance = CanSetStateAxisResponse.__new__(
            CanSetStateAxisResponse
        )  # type: CanSetStateAxisResponse
        instance.error = pb_data.error
        instance.axis_number = pb_data.axis_number
        return instance
