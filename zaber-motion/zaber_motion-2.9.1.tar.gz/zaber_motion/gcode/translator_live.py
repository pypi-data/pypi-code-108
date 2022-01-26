# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from ..units import Units
from ..ascii import Stream
from .translator_config import TranslatorConfig
from .translate_result import TranslateResult


class TranslatorLive:
    """
    Represents a live G-Code translator.
    It allows to stream G-Code blocks to a connected device.
    It requires a stream to be setup on the device.
    """

    @property
    def translator_id(self) -> int:
        """
        The ID of the translator that serves to identify native resources.
        """
        return self._translator_id

    def __init__(self, translator_id: int):
        self._translator_id = translator_id

    @staticmethod
    def setup(
            stream: Stream,
            config: TranslatorConfig
    ) -> 'TranslatorLive':
        """
        Sets up the translator on top of a provided stream.

        Args:
            stream: The stream to setup the translator on.
                The stream must be already setup in a live or a store mode.
            config: Configuration of the translator.

        Returns:
            New instance of translator.
        """
        request = main_pb2.TranslatorCreateLiveRequest()
        request.device = stream.device.device_address
        request.interface_id = stream.device.connection.interface_id
        request.stream_id = stream.stream_id
        request.config.CopyFrom(TranslatorConfig.to_protobuf(config))
        response = main_pb2.TranslatorCreateResponse()
        call_sync("gcode/create_live", request, response)
        return TranslatorLive(response.translator_id)

    def translate(
            self,
            block: str
    ) -> TranslateResult:
        """
        Translates a single block (line) of G-code.
        The commands are queued in the underlying stream to ensure smooth continues movement.
        Returning of this method indicates that the commands are queued (not necessarily executed).

        Args:
            block: Block (line) of G-code.

        Returns:
            Result of translation containing the commands sent to the device.
        """
        request = main_pb2.TranslatorTranslateRequest()
        request.translator_id = self.translator_id
        request.block = block
        response = main_pb2.TranslatorTranslateResponse()
        call("gcode/translate_live", request, response)
        return TranslateResult.from_protobuf(response)

    async def translate_async(
            self,
            block: str
    ) -> TranslateResult:
        """
        Translates a single block (line) of G-code.
        The commands are queued in the underlying stream to ensure smooth continues movement.
        Returning of this method indicates that the commands are queued (not necessarily executed).

        Args:
            block: Block (line) of G-code.

        Returns:
            Result of translation containing the commands sent to the device.
        """
        request = main_pb2.TranslatorTranslateRequest()
        request.translator_id = self.translator_id
        request.block = block
        response = main_pb2.TranslatorTranslateResponse()
        await call_async("gcode/translate_live", request, response)
        return TranslateResult.from_protobuf(response)

    def set_traverse_rate(
            self,
            traverse_rate: float,
            unit: Units
    ) -> None:
        """
        Sets the speed at which the device moves when traversing (G0).

        Args:
            traverse_rate: The traverse rate.
            unit: Units of the traverse rate.
        """
        request = main_pb2.TranslatorSetTraverseRateRequest()
        request.translator_id = self.translator_id
        request.traverse_rate = traverse_rate
        request.unit = unit.value
        call_sync("gcode/set_traverse_rate", request)

    def set_axis_position(
            self,
            axis: str,
            position: float,
            unit: Units
    ) -> None:
        """
        Sets position of translator's axis.
        Use this method to set position after performing movement outside of the translator.
        This method does not cause any movement.

        Args:
            axis: Letter of the axis.
            position: The position.
            unit: Units of position.
        """
        request = main_pb2.TranslatorSetAxisPositionRequest()
        request.translator_id = self.translator_id
        request.axis = axis
        request.position = position
        request.unit = unit.value
        call_sync("gcode/set_axis_position", request)

    def get_axis_position(
            self,
            axis: str,
            unit: Units
    ) -> float:
        """
        Gets position of translator's axis.
        This method does not query device but returns value from translator's state.

        Args:
            axis: Letter of the axis.
            unit: Units of position.

        Returns:
            Position of translator's axis.
        """
        request = main_pb2.TranslatorGetAxisPositionRequest()
        request.translator_id = self.translator_id
        request.axis = axis
        request.unit = unit.value
        response = main_pb2.TranslatorGetAxisPositionResponse()
        call_sync("gcode/get_axis_position", request, response)
        return response.value

    def set_axis_default_position(
            self,
            axis: str,
            position: float,
            unit: Units
    ) -> None:
        """
        Sets default position of translator's axis.
        This position is used by G28.

        Args:
            axis: Letter of the axis.
            position: The default position.
            unit: Units of position.
        """
        request = main_pb2.TranslatorSetAxisPositionRequest()
        request.translator_id = self.translator_id
        request.axis = axis
        request.position = position
        request.unit = unit.value
        call_sync("gcode/set_axis_default", request)

    @staticmethod
    def __free(
            translator_id: int
    ) -> None:
        """
        Releases native resources of a translator.

        Args:
            translator_id: The ID of the translator.
        """
        request = main_pb2.TranslatorEmptyRequest()
        request.translator_id = translator_id
        call_sync("gcode/free", request)

    def __del__(self) -> None:
        TranslatorLive.__free(self.translator_id)
