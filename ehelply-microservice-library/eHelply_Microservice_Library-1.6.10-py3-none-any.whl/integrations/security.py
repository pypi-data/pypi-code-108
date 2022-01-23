from __future__ import annotations

from fastapi import HTTPException, Header, Depends

import requests

from ehelply_bootstrapper.integrations.integration import Integration

from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from ehelply_microservice_library.integrations.sdk import SDK

from ehelply_python_sdk.services.security.sdk import *


class Security(Integration):
    """
    Security integration is used to talk to the ehelply-security microservice
    """

    def __init__(self) -> None:
        super().__init__("security")

        class IntegratedSDK(SecuritySDK):
            def get_base_url(self) -> str:
                return get_fact_endpoint('ehelply-security')

        self.sdk: IntegratedSDK = IntegratedSDK(
            sdk_configuration=SDK.instance.sdk_configuration,
            requests_session=SDK.instance.requests_session
        )

    def load(self):
        pass

    async def create_encryption_key(self, category: str, secret_key: str):
        return requests.post(
            self.sdk.get_base_url() + "/encryption/categories/{category}/keys".format(category=category),
            headers={'EHELPLY-SECURITY-SECRET-KEY': secret_key}).json()

    async def get_encryption_keys(self, category: str, secret_key: str):
        response = requests.get(
            self.sdk.get_base_url() + "/encryption/categories/{category}/keys".format(category=category),
            headers={'EHELPLY-SECURITY-SECRET-KEY': secret_key})

        return response.json()

    async def verify_key(self, access: str, secret: str, exception_if_unauthorized=True) -> Union[str, bool]:
        try:
            result = await self.sdk.verify_key(access=access, secret=secret)

            if result:
                return result.uuid

        except:
            pass

        if exception_if_unauthorized:
            raise HTTPException(status_code=403, detail="Unauthorized - Denied by eHelply")
        else:
            return False
