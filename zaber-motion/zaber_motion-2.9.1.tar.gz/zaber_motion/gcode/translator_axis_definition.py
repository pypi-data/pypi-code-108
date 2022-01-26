# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class TranslatorAxisDefinition:
    """
    Defines an axis of the translator.
    """

    def __init__(
            self: 'TranslatorAxisDefinition',
            axis_letter: str,
            peripheral_id: int,
            microstep_resolution: int
    ) -> None:
        self._axis_letter = axis_letter
        self._peripheral_id = peripheral_id
        self._microstep_resolution = microstep_resolution

    @property
    def axis_letter(self) -> str:
        """
        Letter of the axis (X,Y,Z,A,B,C,E).
        """

        return self._axis_letter

    @axis_letter.setter
    def axis_letter(self, value: str) -> None:
        self._axis_letter = value

    @property
    def peripheral_id(self) -> int:
        """
        ID of the peripheral.
        """

        return self._peripheral_id

    @peripheral_id.setter
    def peripheral_id(self, value: int) -> None:
        self._peripheral_id = value

    @property
    def microstep_resolution(self) -> int:
        """
        Microstep resolution of the axis.
        """

        return self._microstep_resolution

    @microstep_resolution.setter
    def microstep_resolution(self, value: int) -> None:
        self._microstep_resolution = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.TranslatorAxisDefinition
    ) -> 'TranslatorAxisDefinition':
        instance = TranslatorAxisDefinition.__new__(
            TranslatorAxisDefinition
        )  # type: TranslatorAxisDefinition
        instance.axis_letter = pb_data.axis_letter
        instance.peripheral_id = pb_data.peripheral_id
        instance.microstep_resolution = pb_data.microstep_resolution
        return instance

    @staticmethod
    def to_protobuf(source: 'TranslatorAxisDefinition') -> main_pb2.TranslatorAxisDefinition:
        if not isinstance(source, TranslatorAxisDefinition):
            raise TypeError("Provided value is not TranslatorAxisDefinition.")

        pb_data = main_pb2.TranslatorAxisDefinition()
        pb_data.axis_letter = source.axis_letter
        pb_data.peripheral_id = source.peripheral_id
        pb_data.microstep_resolution = source.microstep_resolution
        return pb_data
