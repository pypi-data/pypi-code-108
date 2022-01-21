from typing import Any

from plugp100.core.methods import taporequest


class LoginDeviceMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("login_device", params)
        self.requestTimeMils = 0
