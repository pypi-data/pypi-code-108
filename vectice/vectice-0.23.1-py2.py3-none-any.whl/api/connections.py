from typing import Optional
from urllib.parse import urlencode

from vectice.api._auth import Auth

from .Page import Page
from .output.connection_output import ConnectionOutput
from .output.paged_response import PagedResponse


class ConnectionApi(Auth):
    def __init__(self, _token: Optional[str] = None, auto_connect=True, allow_self_certificate=True):
        super().__init__(_token=_token, auto_connect=auto_connect, allow_self_certificate=allow_self_certificate)
        self._connection_path = "/metadata/connection/"

    @property
    def api_base_path(self) -> str:
        return self._connection_path

    def _filter_response(self, response: dict):
        copy = response.copy()
        for idx, connection in enumerate(response["items"]):
            current_connection = connection.copy()
            for key, value in current_connection.items():
                if key not in ["name", "id", "type", "status"]:
                    copy["items"][idx].pop(key)
        return copy

    def list_connections(
        self,
        search_name: Optional[str] = None,
        connection_type: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[ConnectionOutput]:
        queries = {"index": page_index, "size": page_size}
        if search_name:
            queries["search"] = search_name
        if connection_type:
            queries["type"] = connection_type
        try:
            response = self._get(self._connection_path + "?" + urlencode(queries))
            connections = self._filter_response(response)
        except Exception as e:
            raise ConnectionError(f"Failed to retrieve connections due to {e}")
        return PagedResponse(
            item_cls=ConnectionOutput,
            total=connections["total"],
            page=connections["page"],
            items=connections["items"],
        )
