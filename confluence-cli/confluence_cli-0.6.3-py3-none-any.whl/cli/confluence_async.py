import asyncio
from json import dumps
from typing import List
from urllib.parse import urlencode

import aiohttp
from aiohttp import BasicAuth, ClientResponse
from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.levels import LogLevel
from atlassian.errors import ApiValueError, ApiNotFoundError

from confluence_cli.cli import ConfluenceWrapper
from confluence_cli.cli.types import Page
from confluence_cli.cli.utils import type_wrap

aiologger = Logger.with_default_handlers(name="aio_confluence_log",
                                         formatter=Formatter(
                                             fmt='%(asctime)s,%(msecs)03d - %(levelname)s - %(filename)s - %(message)s'),
                                         level=LogLevel.INFO)


class ConfluenceAsyncWrapper(object):
    """
    Use:
    async with ConfluenceAsyncWrapper(confluence) as aconflu:
        pages: Pages = await aconflu.async_update_pages(pages=all_pages)
    """

    def __init__(self, confluence_wrapper: ConfluenceWrapper):
        self.confluence_api = confluence_wrapper


    async def __aenter__(self):  # setting up a connection
        self._aio_session = aiohttp.ClientSession(auth=BasicAuth(login=self.confluence_api.username,
                                                                 password=self.confluence_api.password),
                                                  headers=self.confluence_api._session.headers)
        return self

    async def __aexit__(self, *err):  # closing the connection
        await self._aio_session.close()
        self._aio_session = None

    async def async_update_pages(self, pages: List[Page]):
        """Needs to be executed inside confluence async context:

        with async confluence as api:
            await api.async_update_pages ..."""
        tasks = []
        for page in pages:
            tasks.append(asyncio.create_task(self.async_update_page(page.id, page.title,
                                                                    page.version.number,
                                                                    body=page.body_storage,
                                                                    always_update=True)))

        return await asyncio.gather(*tasks)

    async def async_update_page(self, page_id, title, preupdate_version: int,
                                body=None,
                                parent_id=None,
                                type="page",
                                representation="storage",
                                minor_edit=False, version_comment=None, always_update=False):

        aiologger.info('Updating {type} "{title}"'.format(title=title, type=type))

        if not always_update and body is not None \
                and self.confluence_api.is_page_content_is_already_updated(page_id, body, title):
            return self.confluence_api.get_page_by_id(page_id)

        try:
            version = preupdate_version + 1
        except (IndexError, TypeError) as e:
            aiologger.error("Can't find '{title}' {type}!".format(title=title, type=type))
            aiologger.debug(e)
            return None

        data = {
            "id": page_id,
            "type": type,
            "title": title,
            "version": {"number": version, "minorEdit": minor_edit},
        }
        if body is not None:
            data["body"] = self.confluence_api._create_body(body, representation)

        if parent_id:
            data["ancestors"] = [{"type": "page", "id": parent_id}]
        if version_comment:
            data["version"]["message"] = version_comment

        try:
            response = await self.async_put("rest/api/content/{0}".format(page_id), data=data)
        except aiohttp.ClientResponseError as e:
            if e.status == 400:
                raise ApiValueError(
                    "No space or no content type, or setup a wrong version "
                    "type set to content, or status param is not draft and "
                    "status content is current",
                    reason=e,
                )
            if e.status == 404:
                raise ApiNotFoundError("Can not find draft with current content", reason=e)

            raise

        return type_wrap(response)

    async def async_put(
            self,
            path,
            data=None,
            headers=None,
            files=None,
            trailing=None,
            params=None,
            absolute=False,
            advanced_mode=False,
    ):
        response = await self.async_request(
            "PUT",
            path=path,
            data=data,
            headers=headers,
            files=files,
            params=params,
            trailing=trailing,
            absolute=absolute,
        )

        return response

    async def async_request(
            self,
            method="GET",
            path="/",
            data=None,
            json=None,
            flags=None,
            params=None,
            headers=None,
            files=None,
            trailing=None,
            absolute=False,
    ) -> dict:

        url = self.confluence_api.url_joiner(None if absolute else self.confluence_api.url, path, trailing)
        params_already_in_url = True if "?" in url else False
        if params or flags:
            if params_already_in_url:
                url += "&"
            else:
                url += "?"
        if params:
            url += urlencode(params or {})
        if flags:
            url += ("&" if params or params_already_in_url else "") + "&".join(flags or [])
        json_dump = None
        if files is None:
            data = None if not data else dumps(data)
            json_dump = None if not json else dumps(json)
        self.confluence_api.log_curl_debug(method=method, url=url, headers=headers, data=data if data else json_dump)
        headers = headers or self.confluence_api.default_headers
        # * For multi part class aiohttp.FormData(fields, quote_fields=True, charset=None)
        async with self._aio_session.request(method=method,
                                             url=url,
                                             headers=headers,
                                             data=data,
                                             json=json,
                                             proxy=self.confluence_api.proxies["https"],
                                             verify_ssl=self.confluence_api.verify_ssl) as response:
            # response.encoding = "utf-8"
            aiologger.debug("HTTP: {} {} -> {} {}".format(method, path, response.status, response.reason))
            aiologger.debug("HTTP: Response text -> {}".format(response.text))

            response.raise_for_status()
            return await response.json()
