import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import SourceList
from cognite.well_model.models import DeleteSources, Source, SourceItems

logger = logging.getLogger(__name__)


class SourcesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def list(self) -> SourceList:
        """List sources

        Returns:
            SourceList:
        """
        path = self._get_path("/sources")
        response: Response = self.client.get(path)
        source_items: SourceItems = SourceItems.parse_obj(response.json())
        return SourceList(source_items.items)

    def ingest(self, sources: List[Source]) -> SourceList:
        """Ingest sources

        Remember to set merge rules after you have added any new sources.

        Args:
            sources (List[Source])

        Returns:
            SourceList:

        Examples:
            Ingest a source:
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import Source
                >>> wm = CogniteWellsClient()
                >>> source = Source(name="volve", description="My new source")
                >>> response = wm.sources.ingest([source])
        """
        path = self._get_path("/sources")
        json = SourceItems(items=sources).json()
        response: Response = self.client.post(path, json)
        source_items: SourceItems = SourceItems.parse_obj(response.json())
        return SourceList(source_items.items)

    def delete(self, sources: List[Source], recursive: Optional[bool] = False):
        path = self._get_path("/sources/delete")
        json = DeleteSources(items=sources, recursive=recursive).json()
        self.client.post(path, json)
