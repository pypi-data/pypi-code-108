"""
Defines volume and file system desktop object classes.

Volumes and file systems are defined analogously to operating system volumes (sometimes called mounts or drives) and
file systems. File systems are repositories of HEA objects. They may be actual file storage on the server running HEA,
a database, a web service, or a separate file server accessed via standard network protocols like SSH. Volumes provide
a connection to that database or service, possibly passing in credentials. Volumes and file systems are represented by
the Volume and FileSystem classes in this module, respectively. Volumes have a file_system_name attribute with a name
of a FileSystem instance.

Microservices that manage data or application state have a default data store, typically MongoDB, with its connection
information specified in a configuration file. To use the default data store for managing HEA desktop objects, if the
microservice supports it, create a volume with the file_system_name set to DEFAULT_FILE_SYSTEM or None. Or use variants
of the microservice's REST API calls that do not require passing in a volume id.

"""
from abc import ABC
from typing import Optional, TypeVar
from . import root


class FileSystem(root.AbstractDesktopObject, ABC):
    """
    Represents a filesystem, which controls how data is stored and retrieved. In HEA, all filesystems are either
    databases or network file storage. DEFAULT_FILE_SYSTEM is reserved by HEA as a unique file system name and may not
    be used as the name attribute of another file system.
    """
    @property
    def name(self) -> Optional[str]:
        """
        Unique name of the file system. DEFAULT_FILE_SYSTEM is a reserved name and may not be used.
        :return: the name of the file system.
        """
        return self.__name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        if name == DEFAULT_FILE_SYSTEM:
            raise ValueError('DEFAULT_FILE_SYSTEM is a reserved name')
        self.__name = str(name) if name is not None else None


FileSystemTypeVar = TypeVar('FileSystemTypeVar', bound=FileSystem)


class MongoDBFileSystem(FileSystem):
    """
    MongoDB-based file system.
    """

    def __init__(self):
        super().__init__()
        self.__connection_string: Optional[str] = None
        self.__database_name: Optional[str] = None

    @property  # type: ignore
    def connection_string(self) -> Optional[str]:
        """The MongoDB connection string."""
        return self.__connection_string

    @connection_string.setter
    def connection_string(self, connection_string: Optional[str]):
        self.__connection_string = str(connection_string) if connection_string is not None else None

    @property  # type: ignore
    def database_name(self) -> Optional[str]:
        """The MongoDB database name"""
        return self.__database_name

    @database_name.setter
    def database_name(self, database_name: Optional[str]):
        self.__database_name = str(database_name) if database_name is not None else None


class AWSFileSystem(FileSystem):
    """
    AWS-based file system.
    """
    pass


class Volume(root.AbstractDesktopObject):
    """
    A single accessible storage area that stores a single filesystem. Some volumes may require providing credentials in
    order to access them.
    """

    def __init__(self):
        super().__init__()
        self.__file_system_name = DEFAULT_FILE_SYSTEM
        self.__credential_id: Optional[str] = None
        self.__folder_id: Optional[str] = None

    @property  # type: ignore
    def folder_id(self) -> Optional[str]:
        """
        The id of the folder to open when opening this volume.
        """
        return self.__folder_id

    @folder_id.setter
    def folder_id(self, id_) -> None:
        self.__folder_id = str(id_) if id_ is not None else None

    @property  # type: ignore
    def file_system_name(self) -> str:
        """
        The unique name of this volume's file system (a FileSystem object). Defaults to the 'root' file system.
        """
        return self.__file_system_name

    @file_system_name.setter  # type: ignore
    def file_system_name(self, file_system_name: str) -> None:
        self.__file_system_name = str(file_system_name) if file_system_name is not None else DEFAULT_FILE_SYSTEM

    @property  # type: ignore
    def credential_id(self) -> Optional[str]:
        """
        The id of the current user's credentials needed to open this volume (a Credentials object), if any.
        """
        return self.__credential_id

    @credential_id.setter  # type: ignore
    def credential_id(self, credentials_id: Optional[str]) -> None:
        self.__credential_id = str(credentials_id) if credentials_id is not None else None


DEFAULT_FILE_SYSTEM = 'DEFAULT_FILE_SYSTEM'
