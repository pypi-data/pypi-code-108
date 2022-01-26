# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List, Optional
from ..protobufs import main_pb2
from ..measurement import Measurement
from .axis_mapping import AxisMapping


class TranslatorConfig:
    """
    Configuration of translator.
    """

    def __init__(
            self: 'TranslatorConfig',
            traverse_rate: Measurement,
            axes_mapping: Optional[List[AxisMapping]] = None
    ) -> None:
        self._traverse_rate = traverse_rate
        self._axes_mapping = axes_mapping

    @property
    def traverse_rate(self) -> Measurement:
        """
        Speed at which the device moves when traversing (G0).
        """

        return self._traverse_rate

    @traverse_rate.setter
    def traverse_rate(self, value: Measurement) -> None:
        self._traverse_rate = value

    @property
    def axes_mapping(self) -> Optional[List[AxisMapping]]:
        """
        Optional custom mapping of translator axes to stream axes.
        """

        return self._axes_mapping

    @axes_mapping.setter
    def axes_mapping(self, value: Optional[List[AxisMapping]]) -> None:
        self._axes_mapping = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def to_protobuf(source: 'TranslatorConfig') -> main_pb2.TranslatorConfig:
        if not isinstance(source, TranslatorConfig):
            raise TypeError("Provided value is not TranslatorConfig.")

        pb_data = main_pb2.TranslatorConfig()
        pb_data.traverse_rate.CopyFrom(Measurement.to_protobuf(source.traverse_rate))
        if source.axes_mapping is not None:
            pb_data.axes_mapping.extend([AxisMapping.to_protobuf(item) for item in source.axes_mapping])
        return pb_data
