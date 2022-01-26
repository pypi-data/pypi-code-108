"""
Client for talking to rest endpoints
"""
import typing as t

from taktile_client.client import Client
from taktile_client.config import settings
from taktile_client.config import version as cversion
from taktile_client.http_client import API
from taktile_client.model import Model
from taktile_client.rest.endpoint import RestEndpoints
from taktile_client.version import assert_supports_version


class RestClient(Client[RestEndpoints]):
    """
    Rest client for talking to models deployed with Taktile.
    """

    def _url_from_host(self, host: str) -> str:
        if settings.DEBUG:
            return f"http://{host}"
        return f"https://{host}"

    def _initalize_endpoints(
        self, url: str, api_key: t.Optional[str]
    ) -> RestEndpoints:
        info = Model(url=url, api_key=api_key).get_info()

        api = API(api_base=url, api_key=api_key)
        assert_supports_version(
            client_version=cversion, server_version=info.taktile_cli
        )
        return RestEndpoints(api=api, infos=info.endpoints)
