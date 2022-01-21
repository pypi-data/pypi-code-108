from uuid import UUID
from typing import List, Optional, Set, Tuple, Union, Literal

from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.errors import DtlError
from datalogue.models.job import Job
from datalogue.models.pipeline import Pipeline
from datalogue.models.tag import Tag
from datalogue.dtl_utils import _parse_list
from datalogue.models.datastore import (
    Datastore,
    _datastore_from_payload
)


class _TagClient:
    """
    Client to interact with the Tags
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    path_fragments = {
        "datastore": "datastores",
        "pipeline": "streams"
    }
    mappings = {
        "datastore": _datastore_from_payload,
        "pipeline": Pipeline._from_payload
    }
    ENTITY_TYPE = Literal["datastore", "pipeline"]

    def update(self, old_name: str, name: str) -> Union[DtlError, Tag]:
        """
          Updates a tag

          :param id: id of the tag to be updated
          :param name: the updated name to be applied
          :return: Returns Tag object if successful, or DtlError if failed
        """
        searched_tag_rsp = self.search(old_name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        payload = {"name": name}
        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags/{searched_tag_rsp.id}", HttpMethod.PUT, payload
        )

        if isinstance(res, DtlError):
            return res

        return Tag._from_payload(res)

    def search(self, name: str) -> Union[DtlError, Tag]:
        """
            Retrieve a tag by its name.

            :param name: the name of the tag to be searched
            :return: the tag if successful, or a DtlError if failed
        """
        res = self.http_client.make_authed_request(self.service_uri + f"/tags/{name}/search", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Tag._from_payload(res)

    def prefix_search(self, prefix: str) -> Union[DtlError, List[Tag]]:
        """
            Search tags by its prefix.

            :param name: the name of the tag to be searched
            :return: the tag if successful, or a DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags/search",
            HttpMethod.GET,
            params={"starts_with": prefix}
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(Tag._from_payload)(res["tags"])

    def delete(self, name: str) -> Union[DtlError, bool]:
        """
            Delete a tag.

            :param name: the name of the tag to be deleted
            :return: Returns True if successful, or DtlError if failed
        """
        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return True

        res = self.http_client.make_authed_request(self.service_uri + f"/tags/{searched_tag_rsp.id}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res

        return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Tag]]:
        """
            List all tags.

            :param page: page to be retrieved
            :param item_per_page: number of items to be put in a page
            :return: Returns a List of all the available tags if successful, or DtlError if failed
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags?page={page}&size={item_per_page}", HttpMethod.GET
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(Tag._from_payload)(res)

    def _get_path_fragment(self, type: ENTITY_TYPE) -> Union[DtlError, str]:
        path_fragment = self.path_fragments.get(type)
        if path_fragment is None:
            return DtlError(f"Invalid entity type: {type}")
        return path_fragment

    def add_tag(self, entity_id: Union[str, UUID], tag_name: str, type: ENTITY_TYPE) -> Union[DtlError, Datastore, Pipeline]:
        """
        Add tags to datastore.
        :param entity_id: id of entity to update
        :param tag_name: list of tag ids to add to the specified datastore
        :param type: type of the entity
        :return: Returns a datastore object if successful, or DtlError if failed
        """

        fragment = self._get_path_fragment(type)
        if isinstance(fragment, DtlError):
            return DtlError(f"Invalid entity type: {type}")

        res = self.http_client.make_authed_request(
            self.service_uri + f"/{fragment}/{entity_id}/tags", body=[tag_name], method=HttpMethod.PUT,
        )

        if isinstance(res, DtlError):
            return res
        return self.mappings[type](res)

    def remove_tag(self, entity_id: Union[str, UUID], tag_name: str, type: ENTITY_TYPE) -> Union[DtlError, Datastore, Pipeline]:
        """
        Remove tags from datastore.
        :param entity_id: id of entity to update
        :param tag_name: list of tag ids to remove from the specified datastore
        :param type: type of the entity
        :return: Returns a datastore object if successful, or DtlError if failed
        """

        fragment = self._get_path_fragment(type)
        if isinstance(fragment, DtlError):
            return DtlError(f"Invalid entity type: {type}")

        res = self.http_client.make_authed_request(
            self.service_uri + f"/{fragment}/{entity_id}/tags", body=[tag_name], method=HttpMethod.DELETE,
        )

        if isinstance(res, DtlError):
            return res
        return self.mappings[type](res)
