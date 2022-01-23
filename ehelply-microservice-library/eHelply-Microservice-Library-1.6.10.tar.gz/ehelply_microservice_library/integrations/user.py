from __future__ import annotations
from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_microservice_library.integrations.fact import get_fact_endpoint

from ehelply_bootstrapper.utils.state import State
from typing import Union


class User(Integration):
    """
    User integration is used to talk to the ehelply-users microservice
    """

    def __init__(self) -> None:
        super().__init__("user")

        self.m2m = State.integrations.get("m2m")

    def init(self):
        super().init()

    def load(self):
        super().load()

    def get_base_url(self) -> str:
        return get_fact_endpoint('ehelply-users')

    def get_participant(self, participant_uuid: str) -> Union[dict, None]:
        response = self.m2m.requests.get(
            self.get_base_url() + "/participants/" + participant_uuid)

        if response.status_code != 200:
            return None

        return response.json()
