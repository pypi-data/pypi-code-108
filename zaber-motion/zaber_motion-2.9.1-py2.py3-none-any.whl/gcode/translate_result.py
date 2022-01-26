# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List
from ..protobufs import main_pb2
from .translate_message import TranslateMessage


class TranslateResult:
    """
    Represents a result of a G-code block translation.
    """

    @property
    def commands(self) -> List[str]:
        """
        Stream commands resulting from the block.
        """

        return self._commands

    @commands.setter
    def commands(self, value: List[str]) -> None:
        self._commands = value

    @property
    def warnings(self) -> List[TranslateMessage]:
        """
        Messages informing about unsupported codes and features.
        """

        return self._warnings

    @warnings.setter
    def warnings(self, value: List[TranslateMessage]) -> None:
        self._warnings = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.TranslatorTranslateResponse
    ) -> 'TranslateResult':
        instance = TranslateResult.__new__(
            TranslateResult
        )  # type: TranslateResult
        instance.commands = list(pb_data.commands)
        instance.warnings = [TranslateMessage.from_protobuf(item) for item in pb_data.warnings]
        return instance
