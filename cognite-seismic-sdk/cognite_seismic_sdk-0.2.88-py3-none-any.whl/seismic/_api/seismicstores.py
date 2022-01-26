import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import MaybeString, Metadata, get_coverage_spec, get_identifier, get_search_spec
from cognite.seismic.data_classes.api_types import SeismicStore

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import OptionalMap
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        EditSeismicStoreRequest,
        SearchSeismicStoresRequest,
    )


class SeismicStoreAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def search(
        self,
        mode: str = "seismic_store",
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
        get_all: bool = False,
        include_file_info: bool = False,
        include_headers: bool = False,
        include_volume_definitions: bool = False,
        include_coverage: bool = False,
        coverage_crs: MaybeString = None,
        coverage_format: MaybeString = None,
    ) -> Iterable[SeismicStore]:
        """Search for seismic stores.

        Can search all seismic stores included in surveys or directly search seismic stores,
        specified by id, external_id, name, or substrings of external_id or name.
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            mode (str): One of "survey" or "seismic_store".
            id (int|None): Id to search by
            external_id (str|None): External id to search by. NOT IMPLEMENTED
            external_id_substring (str|None): Substring of external id to search by. NOT IMPLEMENTED
            name (str|None): Name to search by
            name_substring (str|None): Substring of name to search by
            get_all (bool): Whether to instead retrieve all visible seismic stores. Equivalent to list().
            include_file_info (bool): If true, the response will include information on the source file.
            include_headers (bool): If true, the response will include headers.
            include_volume_definitions (bool): If false, the response will exclude getting the inline and crossline volume definitions.
            coverage_crs (str|None): If specified, includes the coverage in the given CRS. Either coverage_crs or coverage_format must be specified to retrieve coverage.
            coverage_format (str|None): One of "wkt", "geojson". If specified, includes the coverage as the given format.

        Returns:
            Iterable[:py:class:`~cognite.seismic.data_classes.api_types.SeismicStore`]: The list of matching seismic stores
        """

        if include_coverage:
            raise DeprecationWarning(
                """include_coverage is deprecated. Use coverage_crs and coverage_format instead.
For example, search(coverage_format="wkt") is identical to using include_coverage=True. Refer to the SDK documentation for more info.
"""
            )

        if coverage_crs is not None or coverage_format is not None:
            coverage = get_coverage_spec(coverage_crs, coverage_format)
        else:
            coverage = None

        if get_all:
            req = SearchSeismicStoresRequest()
        else:
            spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)
            if mode == "seismic_store":
                req = SearchSeismicStoresRequest(seismic_store=spec, coverage=coverage)
            elif mode == "survey":
                req = SearchSeismicStoresRequest(survey=spec, coverage=coverage)
            else:
                raise Exception("mode should be one of: survey, seismic_store")

        req.include_file_info = include_file_info
        req.include_headers = include_headers
        req.include_volume_definitions = include_volume_definitions

        results = self.query.SearchSeismicStores(req)
        for s in results:
            yield SeismicStore.from_proto(s)

    def list(
        self, *, include_file_info: bool = False, include_volume_definitions: bool = False
    ) -> Iterable[SeismicStore]:
        """List all visible seismic stores.

        List all visible seismic stores. This is equivalent to calling search() with get_all=true.

        Args:
            include_file_info (bool): (Optional) If true, the response will include information on the source file.
            include_volume_definitions (bool): (Optional) If true, the response will include volume definitions.

        Returns:
            Iterable[:py:class:`~cognite.seismic.data_classes.api_types.SeismicStore`]: The list of visible seismic stores
        """
        return self.search(
            get_all=True, include_file_info=include_file_info, include_volume_definitions=include_volume_definitions
        )

    def get(self, id: int, *, coverage_crs: MaybeString = None, coverage_format: MaybeString = None) -> SeismicStore:
        """Get a seismic store by its id.

        Equivalent to `search(id=id, include_file_info=True, include_headers=True)`.

        Args:
            id (int): The seismic store id to find

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.SeismicStore`
        """
        results = [
            s
            for s in self.search(
                id=id,
                include_file_info=True,
                include_headers=True,
                include_volume_definitions=True,
                coverage_crs=coverage_crs,
                coverage_format=coverage_format,
            )
        ]
        if len(results) == 0:
            raise Exception(f"Could not find the seismic store {id}")
        if len(results) > 1:
            raise Exception("Found too many seismic stores. Please contact support.")
        return results[0]

    def edit(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        new_name: MaybeString = None,
        metadata: Union[Metadata, None] = None,
    ) -> SeismicStore:
        """Edit a seismic store.

        Edit a seismic store, providing the seismic store id.
        The name and the metadata can be edited.

        Args:
            id (int | None): The id of the seismic store
            new_name (str | None): (Optional) If specified, the new name. Provide an empty string to delete the existing name.
            metadata (Dict[str, str] | None): (Optional) If specified, replaces the old metadata with the new one.

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.SeismicStore`:
        """
        identifier = get_identifier(id, external_id)
        request = EditSeismicStoreRequest(seismic_store=identifier)
        if new_name is not None:
            request.name = new_name
        if metadata is not None:
            request.metadata.MergeFrom(OptionalMap(data=metadata))
        return SeismicStore.from_proto(self.query.EditSeismicStore(request))
