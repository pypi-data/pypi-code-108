import json
import os
from typing import Dict, Optional, Tuple, Union

import click

import anyscale
from anyscale.api import (
    ApiClientWrapperExternal,
    ApiClientWrapperInternal,
    AsyncApiClientWrapperExternal,
    configure_open_api_client_headers,
    format_api_exception,
)
from anyscale.cli_logger import BlockLogger
import anyscale.client.openapi_client as openapi_client
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
import anyscale.conf
import anyscale.sdk.anyscale_client as anyscale_client
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf


CREDENTIALS_FILE = "~/.anyscale/credentials.json"


class AuthenticationBlock:
    """
    Class to perform authentication logic. This class should never be instantiated
    directly. Instead call `get_auth_api_client()` to get the cached AuthenticationBlock
    object.
    """

    def __init__(
        self,
        cli_token: Optional[str] = None,
        host: Optional[str] = None,
        use_asyncio: bool = False,
        validate_credentials: bool = True,
        log_output: bool = True,
    ):
        """
        Create an AuthenticationBlock object with the following properties that are useful
        externally: host, credentials, api_client, anyscale_api_client.

        Arguments:
            cli_token (Optional[str]): CLI token that must be prefixed with "sss_". If
                passed, the credentials will not be loaded from the environment variable
                or credentials file.
            host (Optional[str]): Host address of Anyscale. Default host will be used if not
                provided.
            use_asyncio (bool): Use asyncio in anyscale external api client.
            validate_credentials (bool): If set to False, credentials that are passed will not
                be authenticated against the Anyscale host.
        `validate_credentials=False` should only be used when writing internal tests, because
        credentials and the host will not be authenticated against Anyscale if provided.
        """
        self.log = BlockLogger(log_output=log_output)
        self.block_label = "Authenticating"
        self.log.open_block(self.block_label)
        self.host = host or shared_anyscale_conf.ANYSCALE_HOST
        if cli_token is not None:
            self.credentials = cli_token
            cli_token_location = "variable"
        else:
            (
                self.credentials,
                cli_token_location,
            ) = AuthenticationBlock._load_credentials()
        if validate_credentials:
            self._validate_credentials_format(self.credentials)

        self.api_client = self._instantiate_api_client()
        self.anyscale_api_client = self._instantiate_anyscale_client(
            use_asyncio=use_asyncio
        )
        if validate_credentials:
            self._validate_api_client_auth()
        anyscale.conf.CLI_TOKEN = self.credentials
        self.log.info(
            f"Loaded Anyscale authentication token from {cli_token_location}.",
            block_label=self.block_label,
        )
        self.log.close_block(self.block_label)

    def _instantiate_api_client(self,) -> DefaultApi:
        """
        Instantiates client to interact with our frontend APIs
        """
        configuration = openapi_client.Configuration(host=self.host)
        configuration.connection_pool_maxsize = 100

        cookie = f"cli_token={self.credentials}"
        api_client = ApiClientWrapperInternal(configuration, cookie=cookie)
        configure_open_api_client_headers(api_client, "CLI")
        api_instance = openapi_client.DefaultApi(api_client)
        return api_instance

    def _instantiate_anyscale_client(self, use_asyncio=False,) -> AnyscaleApi:
        """
        Instantiates client to interact with our externalized APIs

        Arguments:
            use_asyncio (bool): If this flag is set, the client will run requests in
            a threadpool. Invocations of the api client will return coroutines.
        """
        configuration = anyscale_client.Configuration(host=self.host + "/ext")
        configuration.connection_pool_maxsize = 100

        api_client = (
            ApiClientWrapperExternal(
                configuration, cookie=f"cli_token={self.credentials}"
            )
            if not use_asyncio
            else AsyncApiClientWrapperExternal(
                configuration, cookie=f"cli_token={self.credentials}"
            )
        )
        configure_open_api_client_headers(api_client, "CLI")

        api_instance = anyscale_client.DefaultApi(api_client)
        return api_instance

    def _validate_credentials_format(self, credentials: str) -> None:
        if not credentials.startswith("sss_"):
            url = anyscale.util.get_endpoint("/credentials")
            raise click.ClickException(
                "Your user credentials are invalid. Please go to "
                f"{url} and follow the instructions to properly set your credentials."
            )

    def _validate_api_client_auth(self) -> None:
        """
        Authenticates credentials by calling /api/v2/userinfo. Credentials that
        are valid for the internal product API will also be valid for the external
        API.
        """
        old_raise_structured_exception_val = (
            self.api_client.api_client.raise_structured_exception
        )
        self.api_client.api_client.raise_structured_exception = True
        try:
            self.api_client.get_user_info_api_v2_userinfo_get()
        except ApiExceptionInternal as e:
            if e.status == 401:
                raise click.ClickException(
                    f"Your user credentials are invalid for {anyscale.util.get_endpoint('')}. Please go to "
                    f"{anyscale.util.get_endpoint('/credentials')} and follow the instructions to properly "
                    "set your credentials."
                )
            else:
                format_api_exception(e, "GET", "/api/v2/docs")
        except Exception as e:
            raise e
        finally:
            self.api_client.api_client.raise_structured_exception = (
                old_raise_structured_exception_val
            )

    @staticmethod
    def _load_credentials() -> Tuple[str, str]:
        # The environment variable ANYSCALE_CLI_TOKEN can be used to
        # overwrite the credentials in ~/.anyscale/credentials.json
        env_token = os.environ.get("ANYSCALE_CLI_TOKEN")
        if env_token is not None:
            return env_token, "ANYSCALE_CLI_TOKEN"
        path = os.path.expanduser(CREDENTIALS_FILE)
        if not os.path.exists(path):
            url = anyscale.util.get_endpoint("/credentials")
            host = anyscale.util.get_endpoint("")
            raise click.ClickException(
                "Credentials not found. You need to create an account at {} "
                "and then go to {} and follow the instructions.".format(host, url)
            )
        with open(path) as f:
            try:
                credentials: Dict[str, str] = json.load(f)
            except json.JSONDecodeError:
                msg = (
                    "Unable to load user credentials.\n\nTip: Try creating your "
                    "user credentials again by going to {} and "
                    "following the instructions. If this does not work, "
                    "please contact Anyscale support!".format(
                        anyscale.util.get_endpoint("/credentials")
                    )
                )
                raise click.ClickException(msg)
        received_token = credentials.get("cli_token")
        if received_token is None:
            raise click.ClickException(
                "The credential file is not valid. Please regenerate it by following "
                "the instructions at {}".format(
                    anyscale.util.get_endpoint("/credentials")
                )
            )
        return received_token, CREDENTIALS_FILE


_auth_api_client: Optional[Union[Exception, AuthenticationBlock]] = None


def get_auth_api_client(
    cli_token: Optional[str] = None,
    host: Optional[str] = None,
    use_asyncio: bool = False,
    validate_credentials: bool = True,
    log_output: bool = True,
):
    """
    Function to get global AuthenticationBlock object. The AuthenticationBlock will only be
    instantiated once with the passed parameters from the first call to get_auth_api_client
    and will be cached and returned on subsequent calls. If the first instantiation
    of AuthenticationBlock raises an error, that error will be saved and raised on
    subsequent calls to get_auth_api_client.
    """
    global _auth_api_client
    if isinstance(_auth_api_client, Exception):
        raise _auth_api_client
    if _auth_api_client is None:
        try:
            _auth_api_client = AuthenticationBlock(
                cli_token=cli_token,
                host=host,
                use_asyncio=use_asyncio,
                validate_credentials=validate_credentials,
                log_output=log_output,
            )
        except Exception as e:
            _auth_api_client = e
            raise e
    return _auth_api_client
