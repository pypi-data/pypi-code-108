from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, List, Optional, Union

from .files_metadata import TreeItem, TreeItemType
from .data_resource_schema import DataResourceSchema


class WithFilesMetadataTrait(ABC):
    T = TypeVar("T", bound="WithFilesMetadataTrait")

    @abstractmethod
    def with_metadata(
        self: T,
        name: str,
        id: str = None,
        parentId: Optional[str] = None,
        path: Optional[str] = None,
        type: Optional[Union[TreeItemType, str]] = None,
        size: Optional[int] = None,
        isFolder: Optional[bool] = None,
        children: Optional[List[TreeItem]] = None,
        uri: Optional[str] = None,
        metadata: Optional[DataResourceSchema] = None,
        digest: Optional[str] = None,
        itemCreatedDate: Optional[str] = None,
        itemUpdatedDate: Optional[str] = None,
    ) -> T:
        """
        :param name: the name of the file/s or folder/s
        :param id: the id of the dataset
        :param parentId: the parent id of the file/s or folder/s
        :param path: the path of the file/s or folder/s
        :param type: the type of the file/s or folder/s
        :param size: the size of the file/s or folder/s
        :param children: the children (other files under the file/s or folder/s)
        :param uri: the uri of the file/s or folder/s
        :param metadata: the DataResourceSchema of the file/s or folder/s
        :param digest: the hash of the file or folder
        :param itemCreatedDate: creation date of the file or folder, utc time format is used e.g 'YYYY-MM-DD'
        :param itemUpdatedDate: update date of the file or folder, utc time format is used e.g 'YYYY-MM-DD'

        :return: itself
        """
        pass


@dataclass
class WithFilesMetadata(WithFilesMetadataTrait):
    filesMetadata: Optional[List[TreeItem]] = None

    T = TypeVar("T", bound="WithFilesMetadata")

    def with_metadata(
        self: T,
        name: Optional[str] = None,
        id: Optional[str] = None,
        parentId: Optional[str] = None,
        path: Optional[str] = None,
        type: Optional[Union[TreeItemType, str]] = None,
        size: Optional[int] = None,
        isFolder: Optional[bool] = None,
        children: Optional[List[TreeItem]] = None,
        uri: Optional[str] = None,
        metadata: Optional[DataResourceSchema] = None,
        digest: Optional[str] = None,
        itemCreatedDate: Optional[str] = None,
        itemUpdatedDate: Optional[str] = None,
    ) -> T:
        self.filesMetadata = [
            TreeItem(
                name=name,
                id=id,
                parentId=parentId,
                path=path,
                type=type,
                size=size,
                isFolder=isFolder,
                children=children,  # type: ignore
                uri=uri,
                metadata=metadata,
                digest=digest,
                itemCreatedDate=itemCreatedDate,
                itemUpdatedDate=itemUpdatedDate,
            )
        ]
        return self


class WithDelegatedFilesMetadata(WithFilesMetadataTrait, ABC):
    T = TypeVar("T", bound="WithDelegatedFilesMetadata")

    @abstractmethod
    def _get_delegate(self) -> WithFilesMetadataTrait:
        pass

    def with_metadata(
        self: T,
        name: str,
        id: Optional[str] = None,
        parentId: Optional[str] = None,
        path: Optional[str] = None,
        type: Optional[Union[TreeItemType, str]] = None,
        size: Optional[int] = None,
        isFolder: Optional[bool] = None,
        children: Optional[List[TreeItem]] = None,
        uri: Optional[str] = None,
        metadata: Optional[DataResourceSchema] = None,
        digest: Optional[str] = None,
        itemCreatedDate: Optional[str] = None,
        itemUpdatedDate: Optional[str] = None,
    ) -> T:
        """
        The with metadata method enables the creation of a dataset with metadata from popular cloud storage providers and local files. The
        only required kwarg is name. The other kwargs can be leveraged as needed to create and track dataset versions.

        :param name: the name of the file/s or folder/s
        :param id: the id of the dataset
        :param parentId: the parent id of the file/s or folder/s
        :param path: the path of the file/s or folder/s
        :param type: the type of the file/s or folder/s
        :param size: the size of the file/s or folder/s
        :param children: the children (other files under the file/s or folder/s)
        :param uri: the uri of the file/s or folder/s
        :param metadata: the DataResourceSchema of the file/s or folder/s
        :param digest: the hash of the file or folder
        :param itemCreatedDate: creation date of the file or folder, utc time format is used e.g 'YYYY-MM-DD'
        :param itemUpdatedDate: update date of the file or folder, utc time format is used e.g 'YYYY-MM-DD'

        :return: itself
        """
        self._get_delegate().with_metadata(
            name=name,
            id=id,
            parentId=parentId,
            path=path,
            type=type,
            size=size,
            isFolder=isFolder,
            children=children,
            uri=uri,
            metadata=metadata,
            digest=digest,
            itemCreatedDate=itemCreatedDate,
            itemUpdatedDate=itemUpdatedDate,
        )
        return self
