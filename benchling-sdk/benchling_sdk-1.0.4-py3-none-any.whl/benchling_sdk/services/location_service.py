from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.locations import (
    archive_locations,
    bulk_get_locations,
    create_location,
    get_location,
    list_locations,
    unarchive_locations,
    update_location,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    ListLocationsSort,
    Location,
    LocationCreate,
    LocationsArchivalChange,
    LocationsArchive,
    LocationsArchiveReason,
    LocationsPaginatedList,
    LocationsUnarchive,
    LocationUpdate,
)
from benchling_sdk.services.base_service import BaseService


class LocationService(BaseService):
    """
    Locations.

    Manage locations objects. Like all storage, every Location has a barcode that is unique across the registry.

    See https://benchling.com/api/reference#/Locations
    """

    @api_method
    def get_by_id(self, location_id: str) -> Location:
        """
        Get a location by ID.

        See https://benchling.com/api/reference#/Locations/getLocation
        """
        response = get_location.sync_detailed(client=self.client, location_id=location_id)
        return model_from_detailed(response)

    @api_method
    def _locations_page(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListLocationsSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
    ) -> Response[LocationsPaginatedList]:
        return list_locations.sync_detailed(  # type: ignore
            client=self.client,
            sort=none_as_unset(sort),
            schema_id=none_as_unset(schema_id),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ancestor_storage_id=none_as_unset(ancestor_storage_id),
            archive_reason=none_as_unset(archive_reason),
            ids=none_as_unset(optional_array_query_param(ids)),
            barcodes=none_as_unset(optional_array_query_param(barcodes)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListLocationsSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Location]:
        """
        List locations.

        See https://benchling.com/api/reference#/Locations/listLocations
        """

        def api_call(next_token: NextToken) -> Response[LocationsPaginatedList]:
            return self._locations_page(
                sort=sort,
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ancestor_storage_id=ancestor_storage_id,
                archive_reason=archive_reason,
                ids=ids,
                barcodes=barcodes,
                names_any_of=names_any_of,
                schema_fields=schema_fields,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: LocationsPaginatedList) -> Optional[List[Location]]:
            return body.locations

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(
        self, *, location_ids: Optional[Iterable[str]] = None, barcodes: Optional[Iterable[str]] = None
    ) -> Optional[List[Location]]:
        """
        Bulk get locations.

        See https://benchling.com/api/reference#/Locations/bulkGetLocations
        """
        location_id_string = optional_array_query_param(location_ids)
        barcode_string = optional_array_query_param(barcodes)
        response = bulk_get_locations.sync_detailed(
            client=self.client,
            location_ids=none_as_unset(location_id_string),
            barcodes=none_as_unset(barcode_string),
        )
        locations_list = model_from_detailed(response)
        return locations_list.locations

    @api_method
    def create(self, location: LocationCreate) -> Location:
        """
        Create a location.

        See https://benchling.com/api/reference#/Locations/createLocation
        """
        response = create_location.sync_detailed(client=self.client, json_body=location)
        return model_from_detailed(response)

    @api_method
    def update(self, location_id: str, location: LocationUpdate) -> Location:
        """
        Update a location.

        See https://benchling.com/api/reference#/Locations/updateLocation
        """
        response = update_location.sync_detailed(
            client=self.client, location_id=location_id, json_body=location
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, location_ids: Iterable[str], reason: LocationsArchiveReason, should_remove_barcodes: bool
    ) -> LocationsArchivalChange:
        """
        Archive locations.

        See https://benchling.com/api/reference#/Locations/archiveLocations
        """
        archive_request = LocationsArchive(
            location_ids=list(location_ids), reason=reason, should_remove_barcodes=should_remove_barcodes
        )
        response = archive_locations.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, location_ids: Iterable[str]) -> LocationsArchivalChange:
        """
        Unarchive locations.

        See https://benchling.com/api/reference#/Locations/unarchiveLocations
        """
        unarchive_request = LocationsUnarchive(location_ids=list(location_ids))
        response = unarchive_locations.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
