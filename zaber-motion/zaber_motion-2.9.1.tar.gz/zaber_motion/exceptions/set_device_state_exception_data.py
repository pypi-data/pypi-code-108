# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List
from ..protobufs import main_pb2
from .set_peripheral_state_exception_data import SetPeripheralStateExceptionData


class SetDeviceStateExceptionData:
    """
    Contains additional data for a SetDeviceStateFailedException.
    """

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
    def stream_buffers(self) -> List[str]:
        """
        The reason the stream buffers could not be set.
        """

        return self._stream_buffers

    @stream_buffers.setter
    def stream_buffers(self, value: List[str]) -> None:
        self._stream_buffers = value

    @property
    def triggers(self) -> List[str]:
        """
        The reason the triggers could not be set.
        """

        return self._triggers

    @triggers.setter
    def triggers(self, value: List[str]) -> None:
        self._triggers = value

    @property
    def peripherals(self) -> List[SetPeripheralStateExceptionData]:
        """
        Errors for any peripherals that could not be set.
        """

        return self._peripherals

    @peripherals.setter
    def peripherals(self, value: List[SetPeripheralStateExceptionData]) -> None:
        self._peripherals = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.SetDeviceStateExceptionData
    ) -> 'SetDeviceStateExceptionData':
        instance = SetDeviceStateExceptionData.__new__(
            SetDeviceStateExceptionData
        )  # type: SetDeviceStateExceptionData
        instance.settings = list(pb_data.settings)
        instance.stream_buffers = list(pb_data.stream_buffers)
        instance.triggers = list(pb_data.triggers)
        instance.peripherals = [SetPeripheralStateExceptionData.from_protobuf(item) for item in pb_data.peripherals]
        return instance
