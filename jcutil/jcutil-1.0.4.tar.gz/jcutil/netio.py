import aiohttp
import json
from io import BytesIO


async def get_json(url, params, **kwargs):
    """
    GET method with json result
    Parameters
    ----------
    url
    params
    kwargs

    Returns
    -------

    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,
                               headers={'content-type': 'application/json'},
                               **kwargs) as resp:
            if resp.content_type == 'application/json':
                return await resp.json()
            else:
                return json.loads(await resp.text())


async def post_json(url, body, **kwargs):
    """
    post a json body with json result
    Parameters
    ----------
    url
    body
    kwargs dict

    Returns
    -------

    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, **kwargs) as resp:
            return await resp.json()


async def download(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               **kwargs) as resp:
            if resp.status >= 400:
                return None, None
            return BytesIO(await resp.content.read()), resp.content_type
