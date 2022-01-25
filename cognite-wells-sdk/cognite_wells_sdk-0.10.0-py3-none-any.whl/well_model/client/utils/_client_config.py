import os
import pprint
from typing import Callable, Dict, List, Optional, Union

from cognite.well_model.client.utils._token_generator import TokenGenerator
from cognite.well_model.client.utils.exceptions import CogniteAPIKeyError


class _DefaultConfig:
    def __init__(self):
        # Per client
        self.api_key: Optional[str] = os.getenv("COGNITE_API_KEY")
        self.project: Optional[str] = os.getenv("COGNITE_PROJECT")
        self.base_url: str = os.getenv("COGNITE_BASE_URL", "https://api.cognitedata.com")
        self.client_name: Optional[str] = os.getenv("COGNITE_CLIENT_NAME")
        self.max_workers: int = 10
        self.headers: Dict[str, str] = {}
        self.timeout: int = 60

        # Tokens
        self.token_client_id: Optional[str] = os.getenv("COGNITE_CLIENT_ID")
        self.token_client_secret: Optional[str] = os.getenv("COGNITE_CLIENT_SECRET")
        self.token_url: Optional[str] = os.getenv("COGNITE_TOKEN_URL")
        self.token_scopes = os.getenv("COGNITE_TOKEN_SCOPES", "").split(",")
        self.token_custom_args: Dict[str, str] = {}
        # Global
        self.max_retries = 10
        self.max_retry_backoff = 30
        self.max_connection_pool_size = 50
        self.disable_ssl = False


class ClientConfig(_DefaultConfig):
    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        cluster: str = "api",
        client_name: Optional[str] = None,
        base_url: Optional[str] = None,
        max_workers: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        token: Optional[Union[Callable[[], str], str]] = None,
        token_url: Optional[str] = None,
        token_client_id: Optional[str] = None,
        token_client_secret: Optional[str] = None,
        token_scopes: Optional[List[str]] = None,
        token_custom_args: Dict[str, str] = None,
    ):
        super().__init__()

        self.api_key: Optional[str] = api_key or self.api_key
        self.project: str = project or self.project
        self.cluster: str = cluster
        self.max_workers: int = max_workers or self.max_workers
        self.headers: Dict[str, str] = headers or self.headers
        self.timeout: int = timeout or self.timeout

        if client_name is not None:
            self.client_name = client_name
        if self.client_name is None:
            raise ValueError("No client name has been specified in the Cognite Wells Client")

        if base_url:
            self.base_url = base_url.rstrip("/")

        # Tokens
        self.token: Optional[Union[Callable[[], str], str]] = token
        self.token_url = token_url or self.token_url
        self.token_client_id = token_client_id or self.token_client_id
        self.token_client_secret = token_client_secret or self.token_client_secret
        self.token_scopes = token_scopes or self.token_scopes  # type: ignore
        self.token_custom_args = token_custom_args or self.token_custom_args

        if self.api_key is None and self.token is None:
            # If no api_key or token is present; try setting up a token generator
            token_generator = TokenGenerator(
                self.token_url,
                self.token_client_id,
                self.token_client_secret,
                self.token_scopes,
                self.token_custom_args,
            )

            # 'True' if all parameters for generating a token is set
            if token_generator.token_params_set():
                # token is a Callable. If token is about to expire or is 'None', a new token will be generated
                self.token = token_generator.return_access_token

            if self.token is None:
                raise CogniteAPIKeyError("No API key or Token have been specified")

    def __str__(self):
        """ overloading the printing of the class """
        attr = self.__dict__.copy()
        if "api_key" in attr:
            del attr["api_key"]
        return pprint.pformat(attr, indent=4)
