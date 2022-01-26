# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List
from ..protobufs import main_pb2
from .translator_axis_definition import TranslatorAxisDefinition


class TranslatorDefinition:
    """
    Defines an axis of the translator.
    """

    def __init__(
            self: 'TranslatorDefinition',
            device_id: int,
            axes: List[TranslatorAxisDefinition]
    ) -> None:
        self._device_id = device_id
        self._axes = axes

    @property
    def device_id(self) -> int:
        """
        Device ID of the controller.
        Can be obtained from device settings.
        """

        return self._device_id

    @device_id.setter
    def device_id(self, value: int) -> None:
        self._device_id = value

    @property
    def axes(self) -> List[TranslatorAxisDefinition]:
        """
        Axes of translator.
        """

        return self._axes

    @axes.setter
    def axes(self, value: List[TranslatorAxisDefinition]) -> None:
        self._axes = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def to_protobuf(source: 'TranslatorDefinition') -> main_pb2.TranslatorDefinition:
        if not isinstance(source, TranslatorDefinition):
            raise TypeError("Provided value is not TranslatorDefinition.")

        pb_data = main_pb2.TranslatorDefinition()
        pb_data.device_id = source.device_id
        if source.axes is not None:
            pb_data.axes.extend([TranslatorAxisDefinition.to_protobuf(item) for item in source.axes])
        return pb_data
