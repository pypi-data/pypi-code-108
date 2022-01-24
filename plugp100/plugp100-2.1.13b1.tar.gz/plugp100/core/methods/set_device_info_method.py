from . import taporequest
from typing import Any


class SetDeviceInfoMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("set_device_info", params)
