from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Union
from enum import EnumMeta

from .data_resource_schema import DataResourceSchema


class TreeItemType(EnumMeta):
    Folder = "Folder"
    CsvFile = "CsvFile"
    ImageFile = "ImageFile"
    ExcelFile = "ExcelFile"
    TextFile = "TextFile"
    MdFile = "MdFile"
    DataSet = "DataSet"
    DataTable = "DataTable"
    File = "File"
    Notebook = "Notebook"


@dataclass
class TreeItem:
    name: Optional[str] = None
    id: Optional[str] = None
    parentId: Optional[str] = None
    path: Optional[str] = None
    type: Optional[Union[TreeItemType, str]] = None
    isFolder: Optional[bool] = False
    children: List[TreeItem] = field(default_factory=list)
    size: Optional[int] = 0
    uri: Optional[str] = None
    metadata: Optional[DataResourceSchema] = None
    digest: Optional[str] = None
    itemCreatedDate: Optional[str] = None
    itemUpdatedDate: Optional[str] = None

    def append(self, child):
        return self.children.append(child)
