from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.boxes import (
    archive_boxes,
    bulk_get_boxes,
    create_box,
    get_box,
    list_box_contents,
    list_boxes,
    unarchive_boxes,
    update_box,
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
)
from benchling_sdk.models import (
    Box,
    BoxContentsPaginatedList,
    BoxCreate,
    BoxesArchivalChange,
    BoxesArchive,
    BoxesArchiveReason,
    BoxesPaginatedList,
    BoxesUnarchive,
    BoxUpdate,
    ContainerWithCoordinates,
    ListBoxesSort,
)
from benchling_sdk.services.base_service import BaseService


class BoxService(BaseService):
    """
    Boxes.

    Boxes are a structured storage type, consisting of a grid of positions that can each hold one container.
    Unlike locations, there are a maximum number of containers that a box can hold (one per position).

    Boxes are all associated with schemas, which define the type of the box (e.g. "10x10 Cryo Box") along
    with the fields that are tracked and the dimensions of the box.

    Like all storage, every Box has a barcode that is unique across the registry.
    """

    @api_method
    def get_by_id(self, box_id: str) -> Box:
        """
        Get a box.

        See https://benchling.com/api/reference#/Boxes/getBox
        """
        response = get_box.sync_detailed(client=self.client, box_id=box_id)
        return model_from_detailed(response)

    @api_method
    def _boxes_page(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListBoxesSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        empty_positions: Optional[int] = None,
        empty_positions_gte: Optional[int] = None,
        empty_positions_gt: Optional[int] = None,
        empty_positions_lte: Optional[int] = None,
        empty_positions_lt: Optional[int] = None,
        empty_containers: Optional[int] = None,
        empty_containers_gte: Optional[int] = None,
        empty_containers_gt: Optional[int] = None,
        empty_containers_lte: Optional[int] = None,
        empty_containers_lt: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
    ) -> Response[BoxesPaginatedList]:
        return list_boxes.sync_detailed(  # type: ignore
            client=self.client,
            sort=none_as_unset(sort),
            schema_id=none_as_unset(schema_id),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ancestor_storage_id=none_as_unset(ancestor_storage_id),
            storage_contents_id=none_as_unset(storage_contents_id),
            storage_contents_ids=none_as_unset(optional_array_query_param(storage_contents_ids)),
            empty_positions=none_as_unset(empty_positions),
            empty_positionsgte=none_as_unset(empty_positions_gte),
            empty_positionsgt=none_as_unset(empty_positions_gt),
            empty_positionslte=none_as_unset(empty_positions_lte),
            empty_positionslt=none_as_unset(empty_positions_lt),
            empty_containers=none_as_unset(empty_containers),
            empty_containersgte=none_as_unset(empty_containers_gte),
            empty_containersgt=none_as_unset(empty_containers_gt),
            empty_containerslte=none_as_unset(empty_containers_lte),
            empty_containerslt=none_as_unset(empty_containers_lt),
            ids=none_as_unset(optional_array_query_param(ids)),
            barcodes=none_as_unset(optional_array_query_param(barcodes)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            archive_reason=none_as_unset(archive_reason),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListBoxesSort] = None,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ancestor_storage_id: Optional[str] = None,
        storage_contents_id: Optional[str] = None,
        storage_contents_ids: Optional[List[str]] = None,
        empty_positions: Optional[int] = None,
        empty_positions_gte: Optional[int] = None,
        empty_positions_gt: Optional[int] = None,
        empty_positions_lte: Optional[int] = None,
        empty_positions_lt: Optional[int] = None,
        empty_containers: Optional[int] = None,
        empty_containers_gte: Optional[int] = None,
        empty_containers_gt: Optional[int] = None,
        empty_containers_lte: Optional[int] = None,
        empty_containers_lt: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
        barcodes: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Box]:
        """
        List boxes.

        See https://benchling.com/api/reference#/Boxes/listBoxes
        """
        check_for_csv_bug_fix("storage_contents_ids", storage_contents_ids)

        def api_call(next_token: NextToken) -> Response[BoxesPaginatedList]:
            return self._boxes_page(
                sort=sort,
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ancestor_storage_id=ancestor_storage_id,
                storage_contents_id=storage_contents_id,
                storage_contents_ids=storage_contents_ids,
                empty_positions=empty_positions,
                empty_positions_gte=empty_positions_gte,
                empty_positions_gt=empty_positions_gt,
                empty_positions_lte=empty_positions_lte,
                empty_positions_lt=empty_positions_lt,
                empty_containers=empty_containers,
                empty_containers_gte=empty_containers_gte,
                empty_containers_gt=empty_containers_gt,
                empty_containers_lte=empty_containers_lte,
                empty_containers_lt=empty_containers_lt,
                ids=ids,
                barcodes=barcodes,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                creator_ids=creator_ids,
                archive_reason=archive_reason,
                schema_fields=schema_fields,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: BoxesPaginatedList) -> Optional[List[Box]]:
            return body.boxes

        return PageIterator(api_call, results_extractor)

    @api_method
    def _box_contents_page(
        self,
        *,
        box_id: str,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[BoxContentsPaginatedList]:
        return list_box_contents.sync_detailed(  # type: ignore
            client=self.client,
            box_id=box_id,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_box_contents(
        self,
        *,
        box_id: str,
        page_size: Optional[int] = 50,
    ) -> PageIterator[ContainerWithCoordinates]:
        """
        List a box's contents.

        See https://benchling.com/api/reference#/Boxes/listBoxContents
        """

        def api_call(next_token: NextToken) -> Response[BoxContentsPaginatedList]:
            return self._box_contents_page(
                box_id=box_id,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: BoxContentsPaginatedList) -> Optional[List[ContainerWithCoordinates]]:
            return body.containers

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(
        self, *, box_ids: Optional[Iterable[str]] = None, barcodes: Optional[Iterable[str]] = None
    ) -> Optional[List[Box]]:
        """
        Bulk get boxes.

        See https://benchling.com/api/reference#/Boxes/bulkGetBoxes
        """
        box_id_string = optional_array_query_param(box_ids)
        barcode_string = optional_array_query_param(barcodes)
        response = bulk_get_boxes.sync_detailed(
            client=self.client, box_ids=none_as_unset(box_id_string), barcodes=none_as_unset(barcode_string)
        )
        boxes_list = model_from_detailed(response)
        return boxes_list.boxes

    @api_method
    def create(self, box: BoxCreate) -> Box:
        """
        Create a box.

        See https://benchling.com/api/reference#/Boxes/createBox
        """
        response = create_box.sync_detailed(client=self.client, json_body=box)
        return model_from_detailed(response)

    @api_method
    def update(self, box_id: str, box: BoxUpdate) -> Box:
        """
        Update a box.

        See https://benchling.com/api/reference#/Boxes/updateBox
        """
        response = update_box.sync_detailed(client=self.client, box_id=box_id, json_body=box)
        return model_from_detailed(response)

    @api_method
    def archive(
        self, box_ids: Iterable[str], reason: BoxesArchiveReason, should_remove_barcodes: bool
    ) -> BoxesArchivalChange:
        """
        Archive boxes and any containers of the boxes.

        See https://benchling.com/api/reference#/Boxes/archiveBoxes
        """
        archive_request = BoxesArchive(
            box_ids=list(box_ids), reason=reason, should_remove_barcodes=should_remove_barcodes
        )
        response = archive_boxes.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, box_ids: Iterable[str]) -> BoxesArchivalChange:
        """
        Unarchive boxes and the containers that were archived along with them.

        See https://benchling.com/api/reference#/Boxes/unarchiveBoxes
        """
        unarchive_request = BoxesUnarchive(box_ids=list(box_ids))
        response = unarchive_boxes.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
