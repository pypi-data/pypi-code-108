"""
This module contains HEA objects supporting items that are openable in the HEA desktop, called data objects (DataObject
below). HEA uses internet MIME types to provide additional information about the type of data in a DataObject. You can
read more about MIME types at https://www.iana.org/assignments/media-types/media-types.xhtml and
https://en.wikipedia.org/wiki/Media_type.

HEA defines the following custom MIME types that are intended only for internal use by the different parts of HEA:

application/x.folder: HEA folders (heaobject.folder.Folder)
application/x.item: HEA items (heaobject.folder.Item)
application/x.data-in-database: Data in a database (heaobject.data.DataInDatabase)
"""

from heaobject import root
from abc import ABC
from typing import List, Optional
from copy import deepcopy


class DataObject(root.AbstractDesktopObject, ABC):
    """
    Interface for data objects, which are objects that are openable in the HEA desktop. The main difference between
    openable and other objects is the addition of two properties: a MIME type property, and a property containing a
    list of the MIME types that the object supports providing when it is opened.
    """

    @property
    def mime_type(self) -> str:
        """
        The object's MIME type. Note that HEA uses '*/x.*' for all HEA-specific private
        MIME types that only need to be understood by the different parts of HEA, such as 'application/x.folder' for
        folders.
        """
        pass


class DataFile(DataObject):

    DEFAULT_MIME_TYPE = 'text/plain'

    def __init__(self):
        super().__init__()
        self.__mime_type = DataFile.DEFAULT_MIME_TYPE
        self.__mime_type_tranforms = []

    @property
    def mime_type(self) -> str:
        return self.__mime_type

    @mime_type.setter
    def mime_type(self, mime_type: str) -> None:
        if mime_type is None:
            self.__mime_type = DataFile.DEFAULT_MIME_TYPE
        else:
            self.__mime_type = str(mime_type)


class DataInDatabase(DataObject):

    def __init__(self):
        super().__init__()

    @property
    def mime_type(self) -> str:
        return 'application/x.data-in-database'
