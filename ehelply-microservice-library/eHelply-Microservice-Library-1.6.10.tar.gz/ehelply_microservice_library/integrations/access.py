from __future__ import annotations

from fastapi import HTTPException, Header, Depends

from ehelply_bootstrapper.integrations.integration import Integration

from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from ehelply_microservice_library.integrations.sdk import SDK

from ehelply_python_sdk.services.access.sdk import *
from ehelply_python_sdk.services.access.auth_rules import AuthRule


class Access(Integration):
    """
    Access integration is used to talk to the ehelply-access microservice
    """

    def __init__(self) -> None:
        super().__init__("access")

        class IntegratedSDK(AccessSDK):
            def get_base_url(self) -> str:
                if self.sdk_configuration.partition_identifier:
                    return get_fact_endpoint('ehelply-access') + "/partitions/" + self.sdk_configuration.partition_identifier

                return get_fact_endpoint('ehelply-access') + "/partitions/" + self.sdk_configuration.project_identifier

        self.sdk: IntegratedSDK = IntegratedSDK(
            sdk_configuration=SDK.instance.sdk_configuration,
            requests_session=SDK.instance.requests_session
        )

    def load(self):
        AuthRule.exception_to_throw = HTTPException(status_code=403, detail="Unauthorized - Denied by eHelply")


