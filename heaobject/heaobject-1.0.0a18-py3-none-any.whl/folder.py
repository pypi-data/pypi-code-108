from .data import DataObject
from .root import AbstractMemberObject, DesktopObject
from typing import Optional, List
import copy


class Folder(DataObject):
    """
    Represents a directory in the HEA desktop.
    """
    def __init__(self):
        super().__init__()

    @property
    def mime_type(self) -> str:
        """
        Read-only. Always returns 'application/x.folder'.
        """
        return 'application/x.folder'


class Item(DataObject):
    """
    Represents an item in a folder. Items contain the actual object being pointed to as a nested
    """
    def __init__(self):
        super().__init__()
        self.__actual_object_type_name: Optional[str] = None
        self.__actual_object_id: Optional[str] = None
        self.__actual_object: Optional[DesktopObject] = None
        self.__folder_id: Optional[str] = None
        self.__volume_id: Optional[str] = None

    @property
    def mime_type(self) -> str:
        return 'application/x.item'


    @property
    def actual_object_type_name(self) -> Optional[str]:
        """
        The name of the type of the actual HEAObject.
        """
        return self.__actual_object_type_name

    @actual_object_type_name.setter
    def actual_object_type_name(self, actual_object_type_name: Optional[str]) -> None:
        self.__actual_object_type_name = str(actual_object_type_name) if actual_object_type_name is not None else None

    @property
    def actual_object_id(self) -> Optional[str]:
        """
        The id of the actual HEAObject.
        """
        return self.__actual_object_id

    @actual_object_id.setter
    def actual_object_id(self, actual_object_id: Optional[str]) -> None:
        self.__actual_object_id = str(actual_object_id) if actual_object_id is not None else None

    @property
    def actual_object(self) -> Optional[DesktopObject]:
        """
        The actual HEAObject.
        """
        return self.__actual_object

    @actual_object.setter
    def actual_object(self, actual_object: Optional[DesktopObject]) -> None:
        self.__actual_object = copy.deepcopy(actual_object)

    @property
    def folder_id(self) -> Optional[str]:
        """
        The id of this item's folder.
        """
        return self.__folder_id

    @folder_id.setter
    def folder_id(self, folder_id: Optional[str]) -> None:
        self.__folder_id = str(folder_id) if folder_id is not None else None

    @property
    def volume_id(self) -> Optional[str]:
        """
        The id of this item's volume.
        """
        return self.__volume_id

    @volume_id.setter
    def volume_id(self, volume_id: Optional[str]) -> None:
        self.__volume_id = str(volume_id) if volume_id is not None else None

