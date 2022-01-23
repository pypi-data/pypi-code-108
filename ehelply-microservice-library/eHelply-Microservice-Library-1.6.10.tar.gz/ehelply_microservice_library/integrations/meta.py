from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from datetime import datetime
from typing import Union
from pydantic import BaseModel
from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from ehelply_microservice_library.integrations.sdk import SDK

from ehelply_python_sdk.services.meta.sdk import *


class Meta(Integration):
    """
    Meta integration is used to talk to the ehelply-meta microservice
    """

    def __init__(self) -> None:
        super().__init__("meta")

        class IntegratedSDK(MetaSDK):
            def get_base_url(self) -> str:
                return get_fact_endpoint('ehelply-meta')

        self.sdk: IntegratedSDK = IntegratedSDK(
            sdk_configuration=SDK.instance.sdk_configuration,
            requests_session=SDK.instance.requests_session
        )

        self.m2m = State.integrations.get("m2m")

    def load(self):
        pass

    def slug(self, name: str):
        """
        Turn a string into a slug
        :param name:
        :return:
        """
        return self.m2m.requests.post(self.get_base_url() + "/slug", json={"name": name}).json()
