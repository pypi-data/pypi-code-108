"""Wrapper to normalize PyGage support."""


import sys
import time

import numpy as np  # type: ignore

from ._exceptions import CompuScopeException
from ._constants import transfer_modes


def compuscope_error_handling(func):
    """Decorator to raise Python exception when appropriate."""

    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, int) and response < 0:
            raise CompuScopeException(response)
        return response

    return inner


class PyGage(object):
    def __init__(self):
        self.initialize()
        self.handle = self.get_system()

    @compuscope_error_handling
    def commit(self):
        """Commit any configuration changes to device."""
        return self.interface.Commit(self.handle)

    @compuscope_error_handling
    def get_acquisition_config(self):
        return self.interface.GetAcquisitionConfig(self.handle)

    @compuscope_error_handling
    def get_channel_config(self, channel_index):
        return self.interface.GetChannelConfig(self.handle, channel_index)

    @compuscope_error_handling
    def get_multiple_rec_average_count(self, count):
        return self.interface.GetMulRecAverageCount(self.handle)

    @compuscope_error_handling
    def get_status(self):
        return self.interface.GetStatus(self.handle)

    @compuscope_error_handling
    def get_trigger_config(self, trigger_index):
        return self.interface.GetTriggerConfig(self.handle, trigger_index)

    @compuscope_error_handling
    def get_system(self):
        # I don't understand what the arguments to this function
        # (the four zeros) do. It's working for me right now.
        # - Blaise 2020-01-09
        handle = self.interface.GetSystem(0, 0, 0, 0)
        return handle

    @compuscope_error_handling
    def get_system_info(self):
        return self.interface.GetSystemInfo(self.handle)

    @compuscope_error_handling
    def initialize(self):
        return self.interface.Initialize()

    @property
    def interface(self):
        if sys.maxsize > 2 ** 32:
            import PyGage3_64 as pg  # type: ignore
        else:
            import PyGage3_32 as pg  # type: ignore
        return pg

    @compuscope_error_handling
    def set_acquisition_config(
        self,
        config
    ):
        return self.interface.SetAcquisitionConfig(self.handle, config)

    @compuscope_error_handling
    def set_channel_config(
        self,
        channel_index,
        config
    ):
        return self.interface.SetChannelConfig(self.handle, channel_index, config)

    @compuscope_error_handling
    def set_trigger_config(
        self,
        trigger_index,
        config
    ):
        # remember, unlike channels trigger indexes do not correspond to physical assigments
        return self.interface.SetTriggerConfig(self.handle, trigger_index, config)

    @compuscope_error_handling
    def set_multiple_rec_average_count(self, number):
        return self.interface.SetMulRecAverageCount(self.handle, number)

    @compuscope_error_handling
    def start_capture(self):
        return self.interface.StartCapture(self.handle)

    @compuscope_error_handling
    def transfer_data(
        self,
        channel_index,
        start_position,
        transfer_length,
        segment_index=1,
        transfer_mode=transfer_modes["default"],
    ):
        return self.interface.TransferData(
            self.handle,
            channel_index,
            transfer_mode,
            segment_index,
            start_position,
            transfer_length,
        )
