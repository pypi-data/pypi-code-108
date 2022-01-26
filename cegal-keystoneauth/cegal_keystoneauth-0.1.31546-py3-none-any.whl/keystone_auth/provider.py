# Copyright 2021 Cegal AS
# All rights reserved

import json
from types import SimpleNamespace

from cegal.keystone_auth import logger, verify_tls
from cegal.keystone_auth.exceptions import NotReachableException, NotRespondingException


# TODO servermock
class _Provider:
    def __init__(self, provider_uri, context) -> None:
        if not context.identity_server.is_uri_allowed(provider_uri, verify_tls):
            raise Exception(
                "Provider must use tls. If you are developing locally you can disable TLS verifaction by setting an environment variable PYVAR_ALLOW_NON_HTTPS='true'."
            )
        elif verify_tls == False:
            logger.warn(
                "TLS checks are disabled, this should only be used in a development scenario!"
            )
        try:
            resp = context.identity_server.openid_configuration(
                provider_uri, verify_tls
            )
        except:
            raise NotReachableException(provider_uri, "address not reachable")

        if resp.status_code != 200:
            raise NotRespondingException(provider_uri, resp)

        try:
            config = json.loads(
                resp.content, object_hook=lambda d: SimpleNamespace(**d)
            )
            self.authorization_endpoint = config.authorization_endpoint
            self.token_endpoint = config.token_endpoint
            self.device_authorization_endpoint = config.device_authorization_endpoint
            self.jwks_uri = config.jwks_uri
            self.userinfo_endpoint = config.userinfo_endpoint
            self.issuer = config.issuer
        except:
            raise Exception(
                f"There was an error retrieving endpoints from the provider: {provider_uri}"
            )
