from typing import Iterable, List, Optional

from benchling_api_client.api.folders import (
    archive_folders,
    create_folder,
    get_folder,
    list_folders,
    unarchive_folders,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    Folder,
    FolderCreate,
    FoldersArchivalChange,
    FoldersArchive,
    FoldersArchiveReason,
    FoldersPaginatedList,
    FoldersUnarchive,
    ListFoldersSection,
    ListFoldersSort,
)
from benchling_sdk.services.base_service import BaseService


class FolderService(BaseService):
    """
    Folders.

    Manage folder objects.

    See https://benchling.com/api/reference#/Folders
    """

    @api_method
    def get_by_id(self, folder_id: str) -> Folder:
        """
        Get a folder by ID.

        See https://benchling.com/api/reference#/Folders/getFolder
        """
        response = get_folder.sync_detailed(client=self.client, folder_id=folder_id)
        return model_from_detailed(response)

    @api_method
    def _folders_page(
        self,
        *,
        sort: Optional[ListFoldersSort] = ListFoldersSort.NAME,
        archive_reason: Optional[str] = None,
        name_includes: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
        project_id: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        section: Optional[ListFoldersSection] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[FoldersPaginatedList]:
        return list_folders.sync_detailed(
            client=self.client,
            sort=none_as_unset(sort),
            archive_reason=none_as_unset(archive_reason),
            name_includes=none_as_unset(name_includes),
            parent_folder_id=none_as_unset(parent_folder_id),
            project_id=none_as_unset(project_id),
            ids=none_as_unset(optional_array_query_param(ids)),
            name=none_as_unset(name),
            section=none_as_unset(section),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListFoldersSort] = None,
        archive_reason: Optional[str] = None,
        name_includes: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
        project_id: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        section: Optional[ListFoldersSection] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Folder]:
        """
        List folders.

        See https://benchling.com/api/reference#/Folders/listFolders
        """

        def api_call(next_token: NextToken) -> Response[FoldersPaginatedList]:
            return self._folders_page(
                sort=sort,
                archive_reason=archive_reason,
                name_includes=name_includes,
                parent_folder_id=parent_folder_id,
                project_id=project_id,
                ids=ids,
                name=name,
                section=section,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: FoldersPaginatedList) -> Optional[List[Folder]]:
            return body.folders

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, folder: FolderCreate) -> Folder:
        """
        Create folder.

        See https://benchling.com/api/reference#/Folders/createFolder
        """
        response = create_folder.sync_detailed(client=self.client, json_body=folder)
        return model_from_detailed(response)

    @api_method
    def archive(self, folder_ids: Iterable[str], reason: FoldersArchiveReason) -> FoldersArchivalChange:
        """
        Archive folders.

        See https://benchling.com/api/reference#/Folders/archiveFolders
        """
        archive_request = FoldersArchive(folder_ids=list(folder_ids), reason=reason)
        response = archive_folders.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, folder_ids: Iterable[str]) -> FoldersArchivalChange:
        """
        Unarchive folders.

        See https://benchling.com/api/reference#/Folders/unarchiveFolders
        """
        unarchive_request = FoldersUnarchive(folder_ids=list(folder_ids))
        response = unarchive_folders.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
