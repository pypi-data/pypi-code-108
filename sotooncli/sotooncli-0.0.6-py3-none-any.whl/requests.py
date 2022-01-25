import sys
from json import JSONDecodeError

import click
import requests
from requests import ConnectionError

from sotooncli.settings import SERVER_HOST

NON_JSON_RESPONSE_ERROR_MSG = "Invalid response, try updating your cache or try later"
ERROR_MSG_500 = "Server Error, please try later"
ERROR_MSG_404 = "Not Found, try updating your cache"
CONNECTION_ERROR_MSG = 'Cannot connect to server.\n\nYou might want to set "SOTOON_SERVER_HOST" to the right address.'
UNKNOWN_ERROR = "unexpected error from server, please try again later"

METADATA_PATH = f"{SERVER_HOST}/api/v1/metadata"
EXEC_PATH = f"{SERVER_HOST}/api/v1/execute"


def make_header(etag):
    headers_dict = {}
    if etag:
        headers_dict["If-None-Match"] = etag
    return headers_dict


def get_etag(headers):
    if "Sotoon-Etag" in headers:
        return headers["Sotoon-Etag"]
    return None


def get_metadata(path="", etag=None):
    url = f"{METADATA_PATH}/sotoon/{path}"
    try:
        res = requests.get(url=url, headers=make_header(etag))
        if res.status_code == 404:
            raise click.ClickException(ERROR_MSG_404)
        elif res.status_code == 500:
            raise click.ClickException(ERROR_MSG_500)
        elif res.status_code == 304:
            return None, etag
        body = res.json()
        if res.status_code != 200 and body["type"] == "error":
            raise click.ClickException(body["error"]["message"])
        return body, get_etag(res.headers)
    except ConnectionError:
        click.echo(CONNECTION_ERROR_MSG)
        sys.exit(1)
    except JSONDecodeError:
        click.echo(NON_JSON_RESPONSE_ERROR_MSG)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(e)
        sys.exit(1)
    except click.ClickException as e:
        click.echo(e)
        sys.exit(1)


def execute(path, params):
    body = {"path": ["sotoon"] + path[1:], "args": params}
    return send_request_from_cli("post", EXEC_PATH, body)


def send_request_from_cli(method, url, body):
    try:
        res = requests.request(method=method, url=url, json=body)
        if res.status_code == 404:  # TODO 404 response is not json
            raise click.ClickException(ERROR_MSG_404)
        body = res.json()
        if res.status_code != 200 and body["type"] == "error":
            raise click.ClickException(body["error"]["message"])
        return body
    except ConnectionError:
        raise click.ClickException(CONNECTION_ERROR_MSG)
    except JSONDecodeError:
        raise click.ClickException(NON_JSON_RESPONSE_ERROR_MSG)
    except KeyError:
        raise click.ClickException(UNKNOWN_ERROR)
