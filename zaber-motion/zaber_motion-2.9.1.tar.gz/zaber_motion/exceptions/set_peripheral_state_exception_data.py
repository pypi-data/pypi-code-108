# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List
from ..protobufs import main_pb2


class SetPeripheralStateExceptionData:
    """
    Contains additional data for a SetPeripheralStateFailedException.
    """

    @property
    def axis_number(self) -> int:
        """
        The number of axis where the exception originated.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def settings(self) -> List[str]:
        """
        A list of settings which could not be set.
        """

        return self._settings

    @settings.setter
    def settings(self, value: List[str]) -> None:
        self._settings = value

    @property
    def servo_tuning(self) -> str:
        """
        The reason servo tuning could not be set.
        """

        return self._servo_tuning

    @servo_tuning.setter
    def servo_tuning(self, value: str) -> None:
        self._servo_tuning = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.SetPeripheralStateExceptionData
    ) -> 'SetPeripheralStateExceptionData':
        instance = SetPeripheralStateExceptionData.__new__(
            SetPeripheralStateExceptionData
        )  # type: SetPeripheralStateExceptionData
        instance.axis_number = pb_data.axis_number
        instance.settings = list(pb_data.settings)
        instance.servo_tuning = pb_data.servo_tuning
        return instance
