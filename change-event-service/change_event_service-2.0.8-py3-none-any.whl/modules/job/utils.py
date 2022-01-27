from dataclasses import dataclass
from typing import Optional

import requests as requests
from pyctuator.health.health_provider import HealthProvider, Status


@dataclass
class JobHealthStatus(HealthProvider):
    status: Status


class JobHealthProvider(HealthProvider):
    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "job"

    def get_health(self) -> JobHealthStatus:
        r = requests.get(f"http://localhost:5000/scheduler")
        if r.json()["running"]:
            return JobHealthStatus(Status.UP)
        else:
            return JobHealthStatus(Status.DOWN)

    def is_supported(self) -> bool:
        return True

