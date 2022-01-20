import requests

from tasq_cli import settings
from tasq_cli.settings import SERVER, TOKEN

logger = None


def make_request(url, post_data={}, files={}, headers={}, json={}):
    global logger
    if not logger:
        logger = settings.get_logger()
    logger.info(f'request url={url} headers={headers} post_data={post_data} json={json}')
    full_url = SERVER + url
    headers = headers.copy()
    headers['Authorization'] = f'BEARER {TOKEN}'
    if post_data or files:
        r = requests.post(
            full_url,
            headers=headers,
            data = post_data,
            files = files,
        )
    elif json:
        r = requests.post(
            full_url,
            headers=headers,
            json=json
        )
    else:
        r = requests.get(
            full_url,
            headers=headers
        )
    if not 200 <= r.status_code < 400:
        logger.error(f"request failed with statue {r.status_code}, text {r.text}")
        r.raise_for_status()
    return r
