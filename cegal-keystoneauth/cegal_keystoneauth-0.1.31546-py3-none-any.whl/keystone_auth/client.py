# Copyright 2021 Cegal AS
# All rights reserved

from cegal.keystone_auth import logger
from cegal.keystone_auth.identityserver import IdentityServer
from cegal.keystone_auth.options import OidcOptions
from cegal.keystone_auth.tokens import _TokenClient
from cegal.keystone_auth.responses import CegalProductTemplate, DefaultPageHandler


class ExternalKeystoneContext:
    _identity_server = IdentityServer()

    @property
    def identity_server(self):
        return self._identity_server

    def request_authcode_url(self, authorize_endpoint, params):
        from urllib.parse import urlencode

        params = urlencode(params)

        url = f"{authorize_endpoint}?{params}"

        import webbrowser

        wb = webbrowser.get()
        wb.open_new(url)


class OidcClient:
    """
    Instantiate an instance of OidcClient with an OidcOptions and optionally a specialised authentication landing page handler.\n

    Example:\n
    options = OidcOptions("my_client_id", "https://identityprovider.domain.com")\n
    client = OidcClient(options)\n

    Then call get_access_token() to get an access token, this method will perform the necessary actions to return the token.\n
    Example:\n
    access_token = client.get_access_token()\n

    The page_handler instance, if provided, should have two methods:

        landing_page() -> returns a tuple of (continue_serving, html)
        get(parsed_url, auth_state) -> returns a tuple of (continue_serving, html)

            `parsed_url` contains all the components of the URL
            `auth_state` is an instance of cegal.keystone_auth.authorize.AuthState and contains the auth_code
    """

    KEYSTONE_URL = "https://keystone.cegal-geo.com/identity"
    KEYSTONE_STG_URL = "https://stg-keystone.cegal-geo.com/identity"
    KEYSTONE_DEV_URL = "https://dev-keystone.cegal-geo.com/identity"

    def __init__(
        self, oidc_options, page_handler=None, context=ExternalKeystoneContext()
    ) -> None:

        if not isinstance(oidc_options, OidcOptions):
            raise TypeError("Options must be an instance of OidcOptions")
        logger.debug(f"OidcClient __init__ {oidc_options}")
        logger.debug("Token storage location: %s", oidc_options.local_storage)
        self._token_client = _TokenClient(
            oidc_options,
            page_handler if page_handler is not None else CegalProductTemplate(),
            context,
        )

    def get_access_token(self):
        return self._token_client.access_token

    def destroy_tokens_for_client(self):
        """
        ONLY USE FOR DEVELOPMENT!\n
        Calling this method will delete in memory and on disk tokens for your client_id.
        """
        self._token_client.delete_tokens()
