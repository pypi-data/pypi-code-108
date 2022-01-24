from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, List, Optional

from .data_resource import DataResource


class WithDataResourcesTrait(ABC):
    T = TypeVar("T", bound="WithDataResourcesTrait")

    @abstractmethod
    def with_resources(self: T, files: Optional[List[str]] = None, folders: Optional[List[str]] = None) -> T:
        """
        :param files: the files to put in the dataset
        :param folders: the folders (and all file in it) to put in the dataset
        :return: itself
        """
        pass


@dataclass
class WithDataResources(WithDataResourcesTrait):
    dataResources: Optional[List[DataResource]] = None

    T = TypeVar("T", bound="WithDataResources")

    def with_resources(self: T, files: Optional[List[str]] = None, folders: Optional[List[str]] = None) -> T:
        if folders is None:
            folders = []
        if files is None:
            files = []
        file_resources = [DataResource.create_item_resource(uri) for uri in files]
        folder_resources = [DataResource.create_folder_resource(uri) for uri in folders]
        self.dataResources = file_resources + folder_resources
        return self


class WithDelegatedDataResources(WithDataResourcesTrait, ABC):
    T = TypeVar("T", bound="WithDelegatedDataResources")

    @abstractmethod
    def _get_delegate(self) -> WithDataResourcesTrait:
        pass

    def with_resources(self: T, files: Optional[List[str]] = None, folders: Optional[List[str]] = None) -> T:
        self._get_delegate().with_resources(files, folders)
        return self
