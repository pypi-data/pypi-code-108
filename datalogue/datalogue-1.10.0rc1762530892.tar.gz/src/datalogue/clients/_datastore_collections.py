from typing import List, Union, Optional
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.datastore_collection import (
    DatastoreCollection,
    _datastore_collection_from_dict,
)
from datalogue.errors import DtlError
from uuid import UUID
from datalogue.dtl_utils import _parse_list
from functools import reduce


class _DatastoreCollectionClient:
    """
    Client to interact with the datastore collection objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, datastore_collection: DatastoreCollection) -> Union[DtlError, DatastoreCollection]:
        """
        Creates the Datastore Collection as specified.

        :param datastore_collection: Datastore Collection to be created
        :return: string with error message if failed, uuid otherwise
        """
        assert isinstance(datastore_collection, DatastoreCollection), "Input is not a Datastore Collection instance."
        # todo?? assert datastore indeed is a datastore

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections", HttpMethod.POST, datastore_collection._as_payload(),
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)

    def update(self, id: UUID, datastore_collection: DatastoreCollection) -> Union[DtlError, bool]:
        """
        Updates the Datastore Collection for the given id

        :param id: Id of the datastore collection to update
        :param datastore_collection: Datastore Collection to be updated
        :return: string with error message if failed, uuid otherwise
        """
        assert isinstance(datastore_collection, DatastoreCollection), "Input is not a Datastore Collection instance."

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(id), HttpMethod.PUT, datastore_collection._as_payload(),
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[DatastoreCollection]]:
        """
        List the Datastore Collection

        :param page: page to be retrieved
        :param item_per_page: number of datastore_collections to be put in a page
        :return: Returns a List of all the available datastore collections or an error message as a string
        """

        res = self.http_client.make_authed_request(
            self.service_uri + f"/datastore-collections?page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(_datastore_collection_from_dict)(res)

    def search(
        self,
        by_name: Optional[List[str]] = None,
        by_description: Optional[List[str]] = None,
        page: int = 1,
        item_per_page: int = 25,
    ) -> Union[DtlError, List[DatastoreCollection]]:
        """
        Search existing datastore collections for a given names. If nothing is defined for names, 
        it returns every datastore collections (basically matches all)

        :param by_name: a list of datastore names
        :param by_description: a list of datastore descriptions
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available datastores or an error message as a string
        """
        queries = {}

        if isinstance(by_name, list):
            queries["name"] = by_name

        if isinstance(by_description, list):
            queries["description"] = by_description

        payload = {
            "queries": queries,
            "from": (page - 1) * item_per_page,
            "size": item_per_page,
            "type": "datastore-collection",
        }

        res = self.http_client.make_authed_request(self.service_uri + "/v2/search", HttpMethod.POST, payload)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_datastore_collection_from_dict)(res["results"])

    def get(self, id: UUID) -> Union[DtlError, DatastoreCollection]:
        """
        From the provided id, get the corresponding Datastore Collection

        :param id: id of the datastore collection to be fetched
        :return:
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(id), HttpMethod.GET
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)

    def delete(self, id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Datastore Collection

        :param id: id of the datastore collection to be deleted
        :return: true if successful, the error otherwise
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(id), HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def add_datastore(
        self, datastore_collection_id: Union[str, UUID], added_datastore_ids: List[Union[UUID, str]],
    ) -> Union[DtlError, DatastoreCollection]:
        """
        Add datastores to a datastore collection. If one or more specified datastores already exists in the collection, this operation will ignore them.

        :param datastore_collection_id: id of the datastore collection that will be updated with new datastore(s)
        :param added_datastore_ids: a list of ids corresponding to the datastores to be added to the datastore collection
        :return: the updated DatastoreCollection object if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(datastore_collection_id) + "/add-datastores",
            HttpMethod.PUT,
            added_datastore_ids,
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)

    def remove_datastore(
        self, datastore_collection_id: Union[str, UUID], removed_datastore_ids: List[Union[UUID, str]],
    ) -> Union[DtlError, DatastoreCollection]:
        """
        Remove datastores from a datastore collection. If one or more specified datastores is not present in the collection, this operation will ignore them.

        :param datastore_collection_id: id of the datastore collection that will be updated
        :param removed_datastore_ids: a list of ids corresponding to the datastores to be removed from the datastore collection
        :return: the updated DatastoreCollection object if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(datastore_collection_id) + "/remove-datastores",
            HttpMethod.PUT,
            removed_datastore_ids,
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)
