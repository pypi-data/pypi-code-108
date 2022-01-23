from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from datetime import datetime
from typing import Union
from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from ehelply_microservice_library.integrations.sdk import SDK

from ehelply_python_sdk.services.notes.sdk import *


class Note(Integration):
    """
    Note integration is used to talk to the ehelply-notes microservice
    """

    def __init__(self) -> None:
        super().__init__("note")

        class IntegratedSDK(NotesSDK):
            def get_base_url(self) -> str:
                return get_fact_endpoint('ehelply-notes')

        self.sdk: IntegratedSDK = IntegratedSDK(
            sdk_configuration=SDK.instance.sdk_configuration,
            requests_session=SDK.instance.requests_session
        )

    def load(self):
        pass
