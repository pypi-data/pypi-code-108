# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class AxisMapping:
    """
    Maps a translator axis to a Zaber stream axis.
    """

    def __init__(
            self: 'AxisMapping',
            axis_letter: str,
            axis_index: int
    ) -> None:
        self._axis_letter = axis_letter
        self._axis_index = axis_index

    @property
    def axis_letter(self) -> str:
        """
        Letter of the translator axis (X,Y,Z,A,B,C,E).
        """

        return self._axis_letter

    @axis_letter.setter
    def axis_letter(self, value: str) -> None:
        self._axis_letter = value

    @property
    def axis_index(self) -> int:
        """
        Index of the stream axis.
        """

        return self._axis_index

    @axis_index.setter
    def axis_index(self, value: int) -> None:
        self._axis_index = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def to_protobuf(source: 'AxisMapping') -> main_pb2.TranslatorAxisMapping:
        if not isinstance(source, AxisMapping):
            raise TypeError("Provided value is not AxisMapping.")

        pb_data = main_pb2.TranslatorAxisMapping()
        pb_data.axis_letter = source.axis_letter
        pb_data.axis_index = source.axis_index
        return pb_data
