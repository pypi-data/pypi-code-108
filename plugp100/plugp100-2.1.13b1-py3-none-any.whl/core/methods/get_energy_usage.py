from . import taporequest
from typing import Any


class GetEnergyUsageMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("get_energy_usage", params)
