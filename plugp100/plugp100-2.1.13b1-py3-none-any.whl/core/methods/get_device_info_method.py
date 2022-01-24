from . import taporequest
from typing import Any


class GetDeviceInfoMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("get_device_info", params)
