import urllib.parse

from benchling_api_client.client import Client


def replace_client_path(client: Client, base_path: str) -> Client:
    """Override a client's base URL with a new path. Does not update scheme, host, or other URL parts."""
    parsed = urllib.parse.urlparse(client.base_url)
    # _replace is not private, it's part of the NamedTuple API but prefixed _ to avoid conflicts
    updated_url = parsed._replace(path=base_path)
    return client.with_base_url(updated_url.geturl())


def v2_alpha_client(client: Client) -> Client:
    """Override a client's base URL with a v2-alpha path."""
    return replace_client_path(client, "api/v2-alpha")


def v2_beta_client(client: Client) -> Client:
    """Override a client's base URL with a v2-beta path."""
    return replace_client_path(client, "api/v2-beta")
