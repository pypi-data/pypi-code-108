from functools import lru_cache, wraps
import json
from typing import Dict, Iterator, Optional

from gql import Client, gql
from gql.transport.exceptions import TransportProtocolError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.websockets import WebsocketsTransport
import requests
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from grid.metadata import __version__
from grid.sdk.auth import Credentials


def humanize_gql_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        # runtime errors are generated if gql returns with an "error" message
        except RuntimeError as e:
            raise e from None

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f'Grid is unreachable. Can you access https://platform.grid.ai ? '
                f'If not, please try again later.'
            ) from None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ConnectionRefusedError('Not authorized. Did you login?') from None
            if e.response.status_code == 500:
                raise ConnectionError('Grid is having issues. Please again later.') from None
            raise ConnectionError(f'We encountered an unknown error. Please try again later. {type(e).__name__}: {e}')

        except requests.exceptions.Timeout:
            raise ConnectionError('The grid platform could not be reached. Are you online?') from None
        except TimeoutError:
            raise RuntimeError(f"Timeout waiting for messages exceeded") from None

        except TransportProtocolError:
            raise ConnectionRefusedError('You are not authorized to use Grid. Did you login?') from None

        # If connection is suddenly closed, indicate that a known error happened.
        except ConnectionClosedError as e:
            raise ConnectionError(f"Interacting with closed connection. Error: {type(e).__name__}") from None
        except ConnectionClosedOK as e:
            raise ConnectionError(
                f"Interacting with properly closed connection. No new "
                f"messages available. Error {type(e).__name__}"
            ) from None

        except Exception as e:
            raise RuntimeError(f"Unhandled error. Please report to the grid team. {type(e).__name__}: {str(e)}")

    return wrapper


@lru_cache(maxsize=None)
@humanize_gql_exceptions
def gql_client(
    url: str,
    creds: Credentials,
    websocket: bool = False,
    *,
    timeout: int = 10,
    headers: Optional[Dict[str, str]] = None
) -> Client:
    """Only create a client instance if there isn't one.

    TODO(rlizzo): re-enable check_version_compatability when versioning is fixed
    """
    if headers is None:
        headers = {}

    headers.update({
        'Content-type': 'application/json',
        'User-Agent': f'grid-api-{__version__}',
        "X-Grid-User": creds.user_id,
        "X-Grid-Key": creds.api_key,
    })

    if websocket:
        _url = url.replace('http://', 'ws://')
        _url = _url.replace('https://', 'wss://')
        _url = _url.replace('graphql', 'subscriptions')
        transport = WebsocketsTransport(url=_url, init_payload=headers)
    else:
        transport = RequestsHTTPTransport(url=url, use_json=True, headers=headers, timeout=timeout, retries=3)

    res = Client(transport=transport, fetch_schema_from_transport=True)
    return res


@humanize_gql_exceptions
def gql_execute(client: Client, query: str, **kwargs) -> dict:
    """Executes a GraphQL query against Grid's API.
    """
    res = client.execute(gql(query), variable_values=kwargs)
    if 'error' in res:
        raise RuntimeError(json.dumps(res['error']))
    return res
