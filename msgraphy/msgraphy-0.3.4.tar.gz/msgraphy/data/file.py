import datetime
from typing import List

from msgraphy.data import graphdataclass
from msgraphy.data.identity import IdentitySet
from msgraphy.data.sharepoint import SharePointIds


@graphdataclass
class ItemReference:
    drive_id: str = None
    drive_type: str = None
    id: str = None
    name: str = None
    path: str = None
    share_id: str = None
    sharepoint_ids: SharePointIds = None
    site_id: str = None


@graphdataclass
class BaseItem:
    id: str = None
    created_by: IdentitySet = None
    created_date_time: datetime = None
    description: str = None
    e_tag: str = None
    last_modified_by: IdentitySet = None
    last_modified_date_time: datetime = None
    name: str = None
    parent_reference: ItemReference = None
    web_url: str = None

    def get_api_reference(self):
        return f"/drives/{self.parent_reference.drive_id}/items/{self.id}"


@graphdataclass
class Drive(BaseItem):
    drive_type: str = None
    following: "DriveItem" = None
    items: List["DriveItem"] = None
    owner: IdentitySet = None
    quota: dict = None
    root: "DriveItem" = None
    sharepoint_ids: SharePointIds = None
    special: List["DriveItem"] = None
    system: str = None

    def get_api_reference(self):
        return f"/drives/{self.id}"


@graphdataclass
class FileSystemInfo:
    created_date_time: datetime = None
    last_accessed_date_time: datetime = None
    last_modified_date_time: datetime = None


@graphdataclass
class FileFacet:
    mime_type: str = None
    hashes: dict = None


@graphdataclass
class FolderView:
    sort_by: str = None
    sort_order: str = None
    view_type: str = None


@graphdataclass
class FolderFacet:
    child_count: int = None
    view: FolderView = None


@graphdataclass
class DriveItem(BaseItem):
    audio: dict = None
    c_tag: str = None
    content: str = None
    deleted: bool = None
    file: FileFacet = None
    file_system_info: FileSystemInfo = None
    folder: FolderFacet = None
    image: dict = None
    location: dict = None
    package: dict = None
    pending_operations: dict = None
    photo: dict = None
    publication: dict = None
    remote_item: "DriveItem" = None
    root: dict = None
    search_result: dict = None
    shared: dict = None
    size: int = None
    special_folder: dict = None
    video: dict = None
    web_dav_url: str = None


@graphdataclass
class DriveList:
    value: List[Drive]

    def __iter__(self):
        return iter(self.value)
