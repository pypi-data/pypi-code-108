import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import MaybeString, Metadata, get_identifier, get_search_spec
from cognite.seismic.data_classes.api_types import Partition

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        CreatePartitionRequest,
        DeletePartitionRequest,
        EditPartitionRequest,
        SearchPartitionsRequest,
    )


class PartitionAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def search(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
        get_all: bool = False,
    ) -> Iterable[Partition]:
        """Search for partitions.

        Can search by id, external_id, name, or substrings of external_id or name.
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            id (int|None): Partition id
            external_id (str|None): Partition external id
            external_id_substring (str|None): Substring of external id to search by
            name (str|None): Partition name
            name_substring (str|None): Substring of name to search by
            get_all (bool): Whether to instead retrieve all visible partitions. Equivalent to list().

        Returns:
            Iterable[Partition]: The list of matching partitions
        """
        spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)

        if get_all:
            req = SearchPartitionsRequest()
        else:
            req = SearchPartitionsRequest(partitions=spec)
        return [Partition.from_proto(p) for p in self.query.SearchPartitions(req)]

    def get(self, id: Optional[int] = None, external_id: Optional[str] = None) -> Partition:
        """
        Retrieve a single partition by id or external id.

        Equivalent to search() using id or external id.

        Args:
            id (int | None): Partition id
            external_id (str | None): Partition external id

        Returns:
            Partition: The given partition
        """
        if id is None and external_id is None:
            raise TypeError("Either the id or the external_id argument must be provided")
        if id is not None and external_id is not None:
            raise TypeError("Specify only one of id and external_id")

        result = self.search(id=id, external_id=external_id)
        if len(result) > 1:
            raise Exception("Internal error: Found too many results. Please contact support.")
        if len(result) == 0:
            raise Exception("Partition not found")
        return result[0]

    def list(self) -> Iterable[Partition]:
        """List all partitions.

        List all visible partitions. This is equivalent to calling search() with get_all=true.

        Returns:
            Iterable[Partition]: All visible partitions
        """

        return self.search(get_all=True)

    def create(self, *, external_id: str, name: str = "") -> Partition:
        """Create a new partition.

        Create a new partition, providing an external id and an optional name.

        Args:
            external_id (str): The external id of the new partition. Must be unique.
            name (str): (Optional) The name of the new partition. If not specified, will display the external id wherever a name is required.

        Returns:
            :py:class:`Partition`: The newly created partition
        """
        createRequest = CreatePartitionRequest(name=name, external_id=external_id)
        return Partition.from_proto(self.query.CreatePartition(createRequest))

    def edit(self, *, new_name: str, id: Optional[int] = None, external_id: MaybeString = None) -> Partition:
        """Edit an existing partition.

        Edit an existing partition by providing either an id or an external id.
        The only parameter that can be edited is the name.

        Args:
            id (int | None): The id of the partition
            external_id (str | None): The external id of the partition
            new_name (str): The new name. Set as an empty string to delete the existing name.

        Returns:
            :py:class:`Partition`: The edited partition
        """
        identifier = get_identifier(id, external_id)
        editRequest = EditPartitionRequest(partition=identifier, new_name=new_name)
        return Partition.from_proto(self.query.EditPartition(editRequest))

    def delete(self, *, id: Union[int, None] = None, external_id: MaybeString = None) -> bool:
        """Delete a partition.

        Delete a partition by providing either an id or an external id.

        Args:
            id (int | None): The id of the partition
            external_id (str | None): The external id of the partition

        Returns:
            bool: Whether the operation succeeded.
        """
        identifier = get_identifier(id, external_id)
        deleteRequest = DeletePartitionRequest(partition=identifier)
        return self.query.DeletePartition(deleteRequest).success
