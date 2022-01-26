# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class GCodeExecutionExceptionData:
    """
    Contains additional data for GCodeExecutionException.
    """

    @property
    def from_block(self) -> int:
        """
        The index in the block string that caused the exception.
        """

        return self._from_block

    @from_block.setter
    def from_block(self, value: int) -> None:
        self._from_block = value

    @property
    def to_block(self) -> int:
        """
        The end index in the block string that caused the exception.
        The end index is exclusive.
        """

        return self._to_block

    @to_block.setter
    def to_block(self, value: int) -> None:
        self._to_block = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.GCodeExecutionExceptionData
    ) -> 'GCodeExecutionExceptionData':
        instance = GCodeExecutionExceptionData.__new__(
            GCodeExecutionExceptionData
        )  # type: GCodeExecutionExceptionData
        instance.from_block = pb_data.from_block
        instance.to_block = pb_data.to_block
        return instance
