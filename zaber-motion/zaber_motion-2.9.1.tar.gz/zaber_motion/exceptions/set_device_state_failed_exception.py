# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .set_device_state_exception_data import SetDeviceStateExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class SetDeviceStateFailedException(MotionLibException):
    """
    Thrown when a device cannot be set to the supplied state.
    """

    @property
    def details(self) -> SetDeviceStateExceptionData:
        """
        Additional data for SetDeviceStateFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, SetDeviceStateExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, SetDeviceStateExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.SetDeviceStateExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = SetDeviceStateExceptionData.from_protobuf(protobuf_obj)
