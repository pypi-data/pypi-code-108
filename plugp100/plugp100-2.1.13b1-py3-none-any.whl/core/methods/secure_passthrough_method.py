from . import taporequest
from typing import Any


class SecurePassthroughMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("securePassthrough", {"request": params})
