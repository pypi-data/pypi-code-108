from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.plates import (
    archive_plates,
    bulk_get_plates,
    create_plate,
    get_plate,
    list_plates,
    unarchive_plates,
    update_plate,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.logging_helpers import check_for_csv_bug_fix
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
    unset_as_none,
)
from benchling_sdk.models import (
    ListPlatesSort,
    Plate,
    PlateCreate,
    PlatesArchivalChange,
    PlatesArchive,
    PlatesArchiveReason,
    PlatesPaginatedList,
    PlatesUnarchive,
    PlateUpdate,
)
from benchling_sdk.services.base_service import BaseService

DEFAULT_PLATE_HTTP_TIMEOUT: float = 30.0


class PlateService(BaseService):
    """
    Plates.

    Plates are a structured storage type, grids of wells that each function like containers. Plates come in two
    types: a traditional "fixed" type, where the wells cannot move, and a "matrix" type. A matrix plate has similar
    functionality to a box, where the containers inside can be moved around and removed altogether.

    Plates are all associated with schemas, which define the type of the plate (e.g. "96 Well Plate") along with
    the fields that are tracked, the dimensions of the plate, and whether or not the plate is a matrix plate or a
    traditional well plate.

    Like all storage, every Plate has a barcode that is unique across the registry.

    See https://benchling.com/api/reference#/Plates
    """

    @api_method
    def get_by_id(self, plate_id: str, returning: Optional[Iterable[str]] = None) -> Plate:
        """
        Get a Plate by ID.

        See https://benchling.com/api/reference#/Plates/getPlate
        """
        returning_string = optional_array_query_param(returning)
        response = get_plate.sync_detailed(
            client=self.client, plate_id=plate_id, returning=none_as_unset(returning_string)
        )
        return model_from_detailed(response)

    @api_method
    def _plates_page(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListPlatesSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
        returning: Optional[Iterable[str]] = None
    ) -> Response[PlatesPaginatedList]:
        timeout_client = self.client.with_timeout(timeout_seconds) if timeout_seconds else self.client
        return list_plates.sync_detailed(  # type: ignore
            client=timeout_client,
            sort=none_as_unset(sort),
            schema_id=none_as_unset(schema_id),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ancestor_storage_id=none_as_unset(ancestor_storage_id),
            storage_contents_id=none_as_unset(storage_contents_id),
            storage_contents_ids=none_as_unset(optional_array_query_param(storage_contents_ids)),
            archive_reason=none_as_unset(archive_reason),
            ids=none_as_unset(optional_array_query_param(ids)),
            barcodes=none_as_unset(optional_array_query_param(barcodes)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
            returning=none_as_unset(optional_array_query_param(returning)),
        )

    def list(
        self,
        *,
        sort: Optional[ListPlatesSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
        timeout_seconds: Optional[float] = DEFAULT_PLATE_HTTP_TIMEOUT,
        returning: Optional[Iterable[str]] = None
    ) -> PageIterator[Plate]:
        """
        List Plates.

        List operations on large plates may take much longer than normal. The timeout_seconds
        parameter will use a higher HTTP timeout than the regular default. Pass a float to override
        it or pass None to use the standard client default.

        See https://benchling.com/api/reference#/Plates/listPlates
        """
        check_for_csv_bug_fix("storage_contents_ids", storage_contents_ids)
        if returning and "nextToken" not in returning:
            returning = list(returning) + ["nextToken"]

        def api_call(next_token: NextToken) -> Response[PlatesPaginatedList]:
            return self._plates_page(
                sort=sort,
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ancestor_storage_id=ancestor_storage_id,
                storage_contents_id=storage_contents_id,
                storage_contents_ids=storage_contents_ids,
                archive_reason=archive_reason,
                ids=ids,
                barcodes=barcodes,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                creator_ids=creator_ids,
                schema_fields=schema_fields,
                next_token=next_token,
                page_size=page_size,
                timeout_seconds=timeout_seconds,
                returning=returning,
            )

        def results_extractor(body: PlatesPaginatedList) -> Optional[List[Plate]]:
            return unset_as_none(body.plates)

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(
        self,
        *,
        plate_ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        timeout_seconds: Optional[float] = DEFAULT_PLATE_HTTP_TIMEOUT,
        returning: Optional[Iterable[str]] = None
    ) -> Optional[List[Plate]]:
        """
        Bulk get Plates.

        Bulk Get operations on large plates may take much longer than normal. The timeout_seconds
        parameter will use a higher HTTP timeout than the regular default. Pass a float to override
        it or pass None to use the standard client default.

        See https://benchling.com/api/reference#/Plates/bulkGetPlates
        """
        timeout_client = self.client.with_timeout(timeout_seconds) if timeout_seconds else self.client
        plate_id_string = optional_array_query_param(plate_ids)
        barcode_string = optional_array_query_param(barcodes)
        returning_string = optional_array_query_param(returning)
        response = bulk_get_plates.sync_detailed(
            client=timeout_client,
            plate_ids=none_as_unset(plate_id_string),
            barcodes=none_as_unset(barcode_string),
            returning=none_as_unset(returning_string),
        )
        plates_list = model_from_detailed(response)
        return plates_list.plates

    @api_method
    def create(self, plate: PlateCreate, returning: Optional[Iterable[str]] = None) -> Plate:
        """
        Create a Plate.

        See https://benchling.com/api/reference#/Plates/createPlate
        """
        returning_string = optional_array_query_param(returning)
        response = create_plate.sync_detailed(
            client=self.client, returning=none_as_unset(returning_string), json_body=plate
        )
        return model_from_detailed(response)

    @api_method
    def update(self, plate_id: str, plate: PlateUpdate, returning: Optional[Iterable[str]] = None) -> Plate:
        """
        Update a Plate.

        See https://benchling.com/api/reference#/Plates/updatePlate
        """
        returning_string = optional_array_query_param(returning)
        response = update_plate.sync_detailed(
            client=self.client, plate_id=plate_id, json_body=plate, returning=none_as_unset(returning_string)
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, plate_ids: Iterable[str], reason: PlatesArchiveReason, should_remove_barcodes: bool
    ) -> PlatesArchivalChange:
        """
        Archive Plates.

        See https://benchling.com/api/reference#/Plates/archivePlates
        """
        archive_request = PlatesArchive(
            plate_ids=list(plate_ids), reason=reason, should_remove_barcodes=should_remove_barcodes
        )
        response = archive_plates.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, plate_ids: Iterable[str]) -> PlatesArchivalChange:
        """
        Unarchive Plates.

        See https://benchling.com/api/reference#/Plates/unarchivePlates
        """
        unarchive_request = PlatesUnarchive(plate_ids=list(plate_ids))
        response = unarchive_plates.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
