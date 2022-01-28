from typing import Iterable, List, Optional

from benchling_api_client.api.entries import (
    archive_entries,
    bulk_get_entries,
    create_entry,
    get_entry,
    get_entry_template,
    get_external_file_metadata,
    list_entries,
    list_entry_templates,
    unarchive_entries,
    update_entry,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    EntriesArchivalChange,
    EntriesArchive,
    EntriesArchiveReason,
    EntriesPaginatedList,
    EntriesUnarchive,
    Entry,
    EntryCreate,
    EntryExternalFile,
    EntryTemplate,
    EntryTemplatesPaginatedList,
    EntryUpdate,
    ListEntriesReviewStatus,
    ListEntriesSort,
)
from benchling_sdk.services.base_service import BaseService


class EntryService(BaseService):
    """
    Entries.

    Entries are rich text documents that allow you to capture all of your experimental data in one place.

    See https://benchling.com/api/reference#/Entries
    """

    @api_method
    def get_entry_by_id(self, entry_id: str) -> Entry:
        """
        Get a notebook entry by ID.

        See https://benchling.com/api/reference#/Entries/getEntry
        """
        response = get_entry.sync_detailed(client=self.client, entry_id=entry_id)
        wrapped_entry = model_from_detailed(response)
        return wrapped_entry.entry

    @api_method
    def _entries_page(
        self,
        *,
        sort: Optional[ListEntriesSort] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        review_status: Optional[ListEntriesReviewStatus] = None,
        mentioned_in: Optional[str] = None,
        mentions: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        display_ids: Optional[Iterable[str]] = None,
        assigned_reviewer_ids_any_of: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[EntriesPaginatedList]:
        return list_entries.sync_detailed(  # type: ignore
            client=self.client,
            sort=none_as_unset(sort),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            project_id=none_as_unset(project_id),
            archive_reason=none_as_unset(archive_reason),
            review_status=none_as_unset(review_status),
            mentioned_in=none_as_unset(mentioned_in),
            mentions=none_as_unset(mentions),
            ids=none_as_unset(optional_array_query_param(ids)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            display_ids=none_as_unset(optional_array_query_param(display_ids)),
            assigned_reviewer_idsany_of=none_as_unset(
                optional_array_query_param(assigned_reviewer_ids_any_of)
            ),
            schema_id=none_as_unset(schema_id),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_entries(
        self,
        *,
        sort: Optional[ListEntriesSort] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        review_status: Optional[ListEntriesReviewStatus] = None,
        mentioned_in: Optional[str] = None,
        mentions: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        display_ids: Optional[Iterable[str]] = None,
        assigned_reviewer_ids_any_of: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Entry]:
        """
        List notebook entries.

        See https://benchling.com/api/reference#/Entries/listEntries
        """

        def api_call(next_token: NextToken) -> Response[EntriesPaginatedList]:
            return self._entries_page(
                sort=sort,
                modified_at=modified_at,
                name=name,
                project_id=project_id,
                archive_reason=archive_reason,
                review_status=review_status,
                mentioned_in=mentioned_in,
                mentions=mentions,
                ids=ids,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                creator_ids=creator_ids,
                display_ids=display_ids,
                assigned_reviewer_ids_any_of=assigned_reviewer_ids_any_of,
                schema_id=schema_id,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: EntriesPaginatedList) -> Optional[List[Entry]]:
            return body.entries

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_external_file(self, entry_id: str, external_file_id: str) -> EntryExternalFile:
        """
        Retrieve the metadata for an external file.

        Use the `download_url` to download the actual file.

        See https://benchling.com/api/reference#/Entries/getExternalFileMetadata
        """
        response = get_external_file_metadata.sync_detailed(
            client=self.client, entry_id=entry_id, external_file_id=external_file_id
        )
        wrapped_file = model_from_detailed(response)
        return wrapped_file.external_file

    @api_method
    def create_entry(self, entry: EntryCreate) -> Entry:
        """
        Create a notebook entry.

        See https://benchling.com/api/reference#/Entries/createEntry
        """
        response = create_entry.sync_detailed(client=self.client, json_body=entry)
        return model_from_detailed(response)

    @api_method
    def update_entry(self, entry_id: str, entry: EntryUpdate) -> Entry:
        """
        Update a notebook entry's metadata.

        See https://benchling.com/api/reference#/Entries/updateEntry
        """
        response = update_entry.sync_detailed(client=self.client, entry_id=entry_id, json_body=entry)
        return model_from_detailed(response)

    @api_method
    def bulk_get_entries(
        self, entry_ids: Optional[Iterable[str]] = None, display_ids: Optional[Iterable[str]] = None
    ) -> Optional[List[Entry]]:
        """
        Bulk get notebook entries.

        See https://benchling.com/api/reference#/Entries/bulkGetEntries
        """
        entry_id_string = optional_array_query_param(entry_ids)
        display_id_string = optional_array_query_param(display_ids)
        response = bulk_get_entries.sync_detailed(
            client=self.client,
            entry_ids=none_as_unset(entry_id_string),
            display_ids=none_as_unset(display_id_string),
        )
        entries = model_from_detailed(response)
        return entries.entries

    @api_method
    def archive_entries(
        self, entry_ids: Iterable[str], reason: EntriesArchiveReason
    ) -> EntriesArchivalChange:
        """
        Archive notebook entries.

        See https://benchling.com/api/reference#/Entries/archiveEntries
        """
        archive_request = EntriesArchive(entry_ids=list(entry_ids), reason=reason)
        response = archive_entries.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive_entries(self, entry_ids: Iterable[str]) -> EntriesArchivalChange:
        """
        Unarchive notebook entries.

        See https://benchling.com/api/reference#/Entries/unarchiveEntries
        """
        unarchive_request = EntriesUnarchive(entry_ids=list(entry_ids))
        response = unarchive_entries.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def _entry_templates_page(
        self,
        *,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        template_collection_id: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[EntryTemplatesPaginatedList]:
        return list_entry_templates.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            template_collection_id=none_as_unset(template_collection_id),
            ids=none_as_unset(optional_array_query_param(ids)),
            schema_id=none_as_unset(schema_id),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_entry_templates(
        self,
        *,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        template_collection_id: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[EntryTemplate]:
        """
        List entry templates.

        See https://benchling.com/api/reference#/Entries/listEntryTemplates
        """

        def api_call(next_token: NextToken) -> Response[EntryTemplatesPaginatedList]:
            return self._entry_templates_page(
                modified_at=modified_at,
                name=name,
                template_collection_id=template_collection_id,
                ids=ids,
                schema_id=schema_id,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: EntryTemplatesPaginatedList) -> Optional[List[EntryTemplate]]:
            return body.entry_templates

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_entry_template_by_id(self, entry_template_id: str) -> EntryTemplate:
        """
        Get a notebook template entry by ID.

        See https://benchling.com/api/reference#/Entries/getTemplateEntry
        """
        # TODO rename get_entry_template
        response = get_entry_template.sync_detailed(client=self.client, entry_template_id=entry_template_id)
        return model_from_detailed(response)
