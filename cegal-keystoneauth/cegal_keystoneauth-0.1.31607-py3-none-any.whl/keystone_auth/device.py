# Copyright 2021 Cegal AS
# All rights reserved

from datetime import datetime, timedelta
from cegal.keystone_auth import logger


class _DeviceClient:
    def __init__(
        self,
        client_id,
        extra_scopes,
        audience,
        token_endpoint,
        device_authorization_endpoint,
        context,
    ) -> None:
        self._context = context
        self.device_authorization_endpoint = device_authorization_endpoint
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.request_scopes = "openid"
        if extra_scopes != None:
            self.request_scopes = self.request_scopes + " " + extra_scopes
        self.audience = audience

    def get_token_with_device_flow(self):
        logger.debug("Attempting device code flow.")
        data = self._request_device_activation()
        return data

    def _request_device_activation(self):
        device_code_response = self._request_device_code()
        logger.debug("Success obtaining device code.")
        code_expired = datetime.now() + timedelta(
            seconds=device_code_response["expires_in"]
        )
        logger.info(
            f"Device login will expire in {device_code_response['expires_in']} seconds"
        )

        # Ask user to login
        print(
            f"Open the page {device_code_response['verification_uri']} in your browser and login in with the code {device_code_response['user_code']}"
        )

        return self._context.identity_server.device_activation(
            self.token_endpoint,
            device_code_response["device_code"],
            self.client_id,
            code_expired,
            device_code_response["interval"],
        )

    def _request_device_code(self):
        r = self._context.identity_server.request_device_code(
            self.device_authorization_endpoint,
            self.client_id,
            self.request_scopes,
            self.audience,
        )
        return r.json()
