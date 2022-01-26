import json
import logging

from atlassian.errors import ApiError
from atlassian.rest_client import AtlassianRestAPI
from requests import HTTPError, Response

from confluence_cli.cli.types import NavigableDict
from confluence_cli.cli.utils import type_wrap

log = logging.getLogger("confluence_log")


class ComalaAPI(AtlassianRestAPI):

    def __init__(self, url, *args, **kwargs):
        if ("atlassian.net" in url or "jira.com" in url) and ("/wiki" not in url):
            url = AtlassianRestAPI.url_joiner(url, "/wiki")
            if "cloud" not in kwargs:
                kwargs["cloud"] = True
        super(ComalaAPI, self).__init__(url, *args, **kwargs)

    def get_page_status(self, page_id: str, expand: str = None) -> NavigableDict:

        url = f"rest/cw/1/content/{page_id}/status"
        log.info(url)
        params = {}
        if expand is not None:
            params["expand"] = expand

        if self.advanced_mode:
            return self.get(url, params=params)
        try:
            response = self.get(url)
        except HTTPError as e:
            if e.response.status_code == 404:
                # Raise ApiError as the documented reason is ambiguous
                raise ApiError("There is no content with the given id, "
                               "or the calling user does not have permission to view the content", reason=e,)
            if e.response.status_code == 204:
                raise ApiError("There is no workflow set on this page", reason=e,)
            raise e

        return type_wrap(response)

    def set_page_state(self, page_id: str, state_name: str) -> NavigableDict:

        url = f"rest/cw/1/content/{page_id}/state"
        log.info(url)
        data = dict()
        data["name"] = state_name
        response: Response = self.put(url, data=data)
        return type_wrap(response)



