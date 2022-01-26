# Copyright 2021 Cegal AS
# All rights reserved
from enum import Enum

from cegal.keystone_auth.utils import local_storage_location


class OidcFlow(Enum):
    """
    An enum to select the oauth flow.\n
    You should mainly be using auth_code which is the default setting.\n
    Where a browser is not available device_code can be used.\n
    The default behaviour for auth_code is to fallback on device_code, if you want to disable this then use auth_code_no_fallback.\n
    client_credentials is not yet implemented but will be in a future release.\n
    """

    auth_code = 0
    auth_code_no_fallback = 1
    device_code = 2
    client_credential = 3


class OidcOptions:
    """
    Create an instance of OidcOptions for passing to the OidcClient object creation.\n
    Options:\n
        client_id       (Required): This is the client_id which identifies your application and will be precreated on the identity provider.\n
        provider_uri    (Required): The fqdn of the identity provider you are authenticating againt, must use https.\n
        extra_scopes    (Optional): openid is added by default. Otherwise add in any extra API scopes you are requesting access to in a list of strings.  Any audiences *must* be listed here as well\n
        audiences       (Optional): Usually if you are requesting extra_scopes they will be associated with an API resource, supply the API resource names here so we can verify the audience claim in the token. If you don't supply anything here and the access token has an audience claim, validation will fail.  Supply single or multiple audiences list of strs\n
        oidc_flow       (Optional): The default is "auth code with PKCE" , this is the preferred flow where possible. If no browser is available then you can use device_code flow. There may also be some exceptions (which need careful consideration) where client credentials are used, then you need to specify OidcFlow.client_credentials.\n
        local_storage   (Optional): Recommended to always leave this default as other products will use the same SQLite database. However the option is there to change in special circumstances where you need to.\n
        no_cache        (Optional): Setting this to True will bypass fetching and storing of tokens to SQLite on disk, only really expected to be used for development purposes when you are changing settings often and need a new token.\n

    n.b. The extra_scopes/audiences are conflated at the moment: OAuth2 just requires the concept of scopes, but Keystone separates them out into audiences which Jwt then verifies.  This portion of the API will change.

    """

    def __init__(
        self,
        client_id=None,
        provider_uri=None,
        extra_scopes=None,
        audiences=None,
        oidc_flow=OidcFlow.auth_code,
        local_storage=None,
        no_cache=False,
    ) -> None:
        if client_id is None:
            raise ValueError("Must supply a client_id")
        if provider_uri is None:
            raise ValueError("Must supply a provider_uri")
        if not isinstance(oidc_flow, OidcFlow):
            raise TypeError("Only auth_code or client_credential are supported")
        if audiences is not None and not isinstance(audiences, list):
            raise TypeError("audiences must be a list")
        if extra_scopes is not None and not isinstance(extra_scopes, list):
            raise TypeError("extra_scopes must be a list")

        if audiences is not None:
            if extra_scopes is None:
                raise ValueError("All audiences must be listed in extra_scopes as well")
            else:
                for aud in audiences:
                    if aud not in extra_scopes:
                        raise ValueError(
                            "All audiences must be listed in extra_scopes as well"
                        )

        if local_storage is None:
            local_storage = local_storage_location()

        self.client_id = client_id
        self.provider_uri = provider_uri
        self.extra_scopes = extra_scopes
        self.audience = audiences
        self.oidc_flow = oidc_flow
        self.local_storage = local_storage
        self.no_cache = no_cache

    def __str__(self):
        d = {
            "client_id": self.client_id,
            "provider_uri": self.provider_uri,
            "extra_scopes": self.extra_scopes,
            "audiences": self.audience,
            "oidc_flow": self.oidc_flow,
            "local_storage": self.local_storage,
            "no_cache": self.no_cache,
        }
        return str(d)

    @staticmethod
    def _construct_audience(audience):
        if isinstance(audience, str):
            return audience
        return " ".join(audience)
