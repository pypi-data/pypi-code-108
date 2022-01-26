import webbrowser
from typing import Optional

import keyring
from oauth2_client.credentials_manager import OAuthError, ServiceInformation
from structlog import get_logger

from .gnista_credential_manager import GnistaCredentialManager

log = get_logger()


# pylint: disable=too-many-instance-attributes
class GnistaConnection:
    scope = ["data-api"]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        base_url: Optional[str] = None,
        datapoint_base_url: Optional[str] = None,
        datasource_base_url: Optional[str] = None,
        authentication_base_url: Optional[str] = None,
        client_id: str = None,
        client_secret: str = None,
        tenant_name: str = None,
        verify_ssl=True,
    ):
        if base_url is None:
            base_url = "https://app.gnista.io"

        if datapoint_base_url is None:
            datapoint_base_url = base_url + "/api/datapoint"

        if datasource_base_url is None:
            datasource_base_url = base_url + "/api/datasource"

        if authentication_base_url is None:
            authentication_base_url = base_url + "/api/authentication"

        self.base_url = base_url
        self.datapoint_base_url = datapoint_base_url
        self.datasource_base_url = datasource_base_url
        self.authentication_base_url = authentication_base_url
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = None
        self.id_token: Optional[str] = None
        self.tenant_name: Optional[str] = tenant_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify_ssl = verify_ssl

    def __str__(self):
        token_available = self.access_token is not None
        return "Gnista Connection to" + self.base_url + " has token: " + token_available

    def _get_base_url(self) -> str:
        return self.base_url

    def get_access_token(self) -> str:
        if self.refresh_token is None:
            # pylint: disable=E1128
            self.refresh_token = self._load_refresh_token()

        if (self.access_token is None or self.id_token is None) and self.refresh_token is None:
            log.info("Starting First Time Login")
            if self.client_id is not None and self.client_secret is not None:
                log.info("Client Credentials Flow")
                self._create_tokens_client_credentials(
                    client_id=self.client_id, client_secret=self.client_secret, scope=self.scope
                )
            else:
                log.info("Auth Code Flow")
                self._create_tokens_code_flow()
        else:
            # refresh with existing refresh token
            if self.refresh_token is not None:
                try:
                    log.info("Using stored refresh Token to Login")
                    self._refresh_tokens(refresh_token=self.refresh_token)
                except OAuthError:
                    log.info("Error using refresh Token, try getting a new one", exc_info=True)
                    if self.client_id is not None and self.client_secret is not None:
                        log.info("Client Credentials Flow")
                        self._create_tokens_client_credentials(
                            client_id=self.client_id, client_secret=self.client_secret, scope=self.scope
                        )
                    else:
                        log.info("Auth Code Flow")
                        self._create_tokens_code_flow()

        if self.access_token is None:
            raise Exception("No Token available")
        return self.access_token

    def _get_service_info(
        self, scope: list = None, client_id: str = "python", client_secret: str = None
    ) -> ServiceInformation:
        if scope is None:
            scope = self.scope

        return ServiceInformation(
            self.authentication_base_url + "/connect/authorize",
            self.authentication_base_url + "/connect/token",
            client_id,
            client_secret,
            scope,
            False,
        )

    def _refresh_tokens(self, refresh_token: str):
        service_information = self._get_service_info()
        manager = GnistaCredentialManager(service_information)
        manager.init_with_token(refresh_token)

        self.tenant_name = manager.tenant_name
        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _create_tokens_code_flow(self, scope: list = None):
        if scope is None:
            scope = self.scope

        scope.append("openid")
        scope.append("profile")
        scope.append("offline_access")

        service_information = self._get_service_info(scope)

        manager = GnistaCredentialManager(service_information)
        # manager.init_with_client_credentials()
        redirect_uri = "http://localhost:4200/home"
        url = manager.init_authorize_code_process(redirect_uri=redirect_uri, state="myState")
        log.info("Authentication has been started. Please follow the link to authenticate with your user:", url=url)
        webbrowser.open(url)

        code = manager.wait_and_terminate_authorize_code_process()
        # From this point the http server is opened on 8080 port and wait to receive a single GET request
        # All you need to do is open the url and the process will go on
        # (as long you put the host part of your redirect uri in your host file)
        # when the server gets the request with the code (or error) in its query parameters

        manager.init_with_authorize_code(redirect_uri, code)
        # Here access and refresh token may be used with self.refresh_token
        self.tenant_name = manager.tenant_name
        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _create_tokens_client_credentials(self, client_id: str, client_secret: str, scope: list = None):
        if scope is None:
            scope = self.scope

        service_information = self._get_service_info(scope, client_id, client_secret)

        manager = GnistaCredentialManager(service_information)
        manager.init_with_client_credentials()

        # Here access and refresh token may be used with self.refresh_token
        self.access_token = manager.access_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _store_refresh_token(self, refresh_token: str):
        pass

    # pylint: disable=R0201
    def _load_refresh_token(self) -> Optional[str]:
        return None


class StaticTokenGnistaConnection(GnistaConnection):
    def __init__(self, base_url: Optional[str] = None, refresh_token: Optional[str] = None):
        super().__init__(base_url=base_url)
        self.refresh_token = refresh_token

    def _store_refresh_token(self, refresh_token: str):
        pass

    def _load_refresh_token(self) -> Optional[str]:
        return self.refresh_token


class KeyringGnistaConnection(GnistaConnection):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        service_name: str = "gnista_library",
        base_url: Optional[str] = None,
        enable_store_refresh_token: bool = True,
        client_id: str = None,
        client_secret: str = None,
        tenant_name: str = None,
    ):
        super().__init__(base_url=base_url, client_id=client_id, client_secret=client_secret, tenant_name=tenant_name)
        self.enable_store_refresh_token = enable_store_refresh_token
        self.service_name = service_name

    def _get_token_name(self):
        return "__refresh_token__:" + super()._get_base_url()

    def clear_stored_token(self):
        keyring.delete_password(self.service_name, self._get_token_name())

    def _store_refresh_token(self, refresh_token: str):
        if self.enable_store_refresh_token:
            pass

        keyring.set_password(self.service_name, self._get_token_name(), refresh_token)

    def _load_refresh_token(self) -> Optional[str]:
        token = keyring.get_password(self.service_name, self._get_token_name())
        return token
