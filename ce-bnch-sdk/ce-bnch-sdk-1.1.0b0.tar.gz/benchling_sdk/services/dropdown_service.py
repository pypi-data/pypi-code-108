from typing import Iterable, List, Optional

from benchling_api_client.api.dropdowns import (
    archive_dropdown_options,
    create_dropdown,
    get_dropdown,
    list_dropdowns,
    unarchive_dropdown_options,
    update_dropdown,
)
from benchling_api_client.models.dropdown_options_archive_reason import DropdownOptionsArchiveReason
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import (
    Dropdown,
    DropdownCreate,
    DropdownOptionsArchivalChange,
    DropdownOptionsArchive,
    DropdownOptionsUnarchive,
    DropdownSummariesPaginatedList,
    DropdownSummary,
    DropdownUpdate,
)
from benchling_sdk.services.base_service import BaseService


class DropdownService(BaseService):
    """
    Dropdowns.

    Dropdowns are registry-wide enums. Use dropdowns to standardize on spelling and naming conventions, especially
    for important metadata like resistance markers.

    See https://benchling.com/api/reference#/Dropdowns
    """

    @api_method
    def get_by_id(self, dropdown_id: str) -> Dropdown:
        """
        Get a dropdown.

        See https://benchling.com/api/reference#/Dropdowns/getDropdown
        """
        response = get_dropdown.sync_detailed(client=self.client, dropdown_id=dropdown_id)
        return model_from_detailed(response)

    @api_method
    def _dropdowns_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[DropdownSummariesPaginatedList]:
        return list_dropdowns.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[DropdownSummary]:
        """
        List dropdowns.

        See https://benchling.com/api/reference#/Dropdowns/listDropdowns
        """

        def api_call(next_token: NextToken) -> Response[DropdownSummariesPaginatedList]:
            return self._dropdowns_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: DropdownSummariesPaginatedList) -> Optional[List[DropdownSummary]]:
            return body.dropdowns

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, dropdown: DropdownCreate) -> Dropdown:
        """
        Create a dropdown.

        See https://benchling.com/api/reference#/Dropdowns/createDropdown
        """
        response = create_dropdown.sync_detailed(client=self.client, json_body=dropdown)
        return model_from_detailed(response)

    @api_method
    def update(self, dropdown_id: str, dropdown: DropdownUpdate) -> Dropdown:
        """
        Update a dropdown.

        See https://benchling.com/api/reference#/Dropdowns/updateDropdown
        """
        response = update_dropdown.sync_detailed(
            client=self.client, dropdown_id=dropdown_id, json_body=dropdown
        )
        return model_from_detailed(response)

    @api_method
    def archive_options(
        self, dropdown_id: str, dropdown_option_ids: Iterable[str], reason: DropdownOptionsArchiveReason
    ) -> DropdownOptionsArchivalChange:
        """
        Archive dropdown options.

        See https://benchling.com/api/reference#/Dropdowns/archiveDropdownOptions
        """
        dropdown_options_archive = DropdownOptionsArchive(
            reason=reason, dropdown_option_ids=list(dropdown_option_ids)
        )
        response = archive_dropdown_options.sync_detailed(
            client=self.client, dropdown_id=dropdown_id, json_body=dropdown_options_archive
        )
        return model_from_detailed(response)

    @api_method
    def unarchive_options(
        self, dropdown_id: str, dropdown_option_ids: Iterable[str]
    ) -> DropdownOptionsArchivalChange:
        """
        Unarchive dropdown options.

        See https://benchling.com/api/reference#/Dropdowns/unarchiveDropdownOptions
        """
        dropdown_options_unarchive = DropdownOptionsUnarchive(dropdown_option_ids=list(dropdown_option_ids))
        response = unarchive_dropdown_options.sync_detailed(
            client=self.client, dropdown_id=dropdown_id, json_body=dropdown_options_unarchive
        )
        return model_from_detailed(response)
