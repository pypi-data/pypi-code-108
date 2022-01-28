import enum
import functools
import hashlib
import stat
from abc import abstractmethod
from datetime import datetime, timedelta, timezone, tzinfo
from typing import AsyncIterable, Dict, Iterable, List, NamedTuple, Optional, Protocol, Tuple, Union
from uuid import UUID, uuid4

import dateutil.tz
from pydantic import BaseModel, Field, validator

# This will either get bumped, or the file will be duplicated and each one will have a VERSION.  In any case this file
# specifies protocol version ...

VERSION = "1.0"

EMPTY_FILE = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
READ_SIZE = (1024**2) * 10

class FileType(enum.Enum):

    REGULAR = "f"
    DIRECTORY = "d"
    CHARACTER_DEVICE = "c"
    BLOCK_DEVICE = "b"
    SOCKET = "s"
    PIPE = "p"
    LINK = "l"


class Inode(BaseModel):
    type: FileType
    mode: int
    modified_time: Optional[datetime]
    size: Optional[int]
    uid: int
    gid: int
    hash: Optional[str] = None

    _MODE_CHECKS = [
        (FileType.REGULAR, stat.S_ISREG),
        (FileType.DIRECTORY, stat.S_ISDIR),
        (FileType.CHARACTER_DEVICE, stat.S_ISCHR),
        (FileType.BLOCK_DEVICE, stat.S_ISBLK),
        (FileType.SOCKET, stat.S_ISSOCK),
        (FileType.PIPE, stat.S_ISFIFO),
        (FileType.LINK, stat.S_ISLNK),
    ]

    @classmethod
    def _type(cls, mode: int) -> FileType:
        # TODO separate this into from_stat() and add a type attribute.
        for file_type, check in cls._MODE_CHECKS:
            if check(mode):
                return file_type
        raise ValueError(f"No type found for mode {mode}")

    @classmethod
    def from_stat(cls, struct_stat, hash_value: Optional[str]) -> "Inode":
        file_type = cls._type(struct_stat.st_mode)
        return Inode(
            mode=stat.S_IMODE(struct_stat.st_mode),
            type=file_type,
            size=struct_stat.st_size if file_type is FileType.REGULAR else None,
            uid=struct_stat.st_uid,
            gid=struct_stat.st_gid,
            modified_time=datetime.fromtimestamp(struct_stat.st_mtime, timezone.utc) \
                            if file_type is FileType.REGULAR else None,
            hash=hash_value,
        )


class DirectoryHash(NamedTuple):
    ref_hash: str
    content: bytes


class Directory(BaseModel):

    __root__: Dict[str, Inode]

    @property
    def children(self):
        return self.__root__

    @children.setter
    def children(self, value: Dict[str, Inode]):
        self.__root__ = value

    def dump(self) -> bytes:
        return self.json(sort_keys=True).encode()

    def hash(self) -> DirectoryHash:
        content = self.dump()
        return DirectoryHash(hash_content(content), content)


class Backup(BaseModel):

    client_id: UUID
    client_name: str
    backup_date: datetime
    started: datetime
    completed: datetime
    roots: Dict[str, Inode]
    description: Optional[str]


class FileReader(Protocol):

    @abstractmethod
    async def read(self, num_bytes: int = None) -> bytes:
        """
        Read n bytes from the source. If N < 0 read all bytes to the EOF before returning.
        """

    @abstractmethod
    def close(self):
        """
        Close the handle to the underlying source.
        """

    @property
    @abstractmethod
    def file_size(self) -> Optional[int]:
        """
        Get the size of this file. May be Null if the item is a pipe or socket.
        """

    def __enter__(self):
        """
        Do nothing on enter
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the file on exit
        """
        self.close()


class DirectoryDefResponse(BaseModel):

    # This will be set on success but not on error
    ref_hash: Optional[str]

    # If defining the directory could not complete because children were missing, the name (not path) of each missing
    # file will be added to missing_files.
    missing_files: List[str] = []

    # Optionally the server can track all directory def requests which have missing files.  BUT something can happen
    # on the client side in between the two directory_def requests.  Eg: a file could be deleted before the client
    # had chance to upload it.  When that happens the second directory_def request will have a different hash to the
    # first.
    # missing_ref is a server-side reference to the previous failed request.  This does not change with content,
    # but may change each request.
    missing_ref: Optional[UUID] = None

    @property
    def success(self) -> bool:
        # If there were no missing files, then the definition was a success.
        # This structure is NOT used to report errors
        return not self.missing_files


class FilterType(enum.Enum):
    INCLUDE = 'include'
    EXCLUDE = 'exclude'
    PATTERN_EXCLUDE = 'exclude-pattern'


class Filter(BaseModel):
    filter: FilterType = Field(...)
    path: str = Field(...)


class ClientConfiguredBackupDirectory(BaseModel):
    base_path: str = Field(...)
    filters: List[Filter] = Field(default_factory=list)


class ClientConfiguration(BaseModel):
    # Friendly name for the client, useful for logging
    client_name: str = Field(...)

    # The id of this client
    client_id: UUID = Field(default_factory=uuid4)

    # Typically set to 1 day or 1 hour.
    backup_granularity: timedelta = Field(timedelta(days=1))

    # backup
    backup_directories: Dict[str, ClientConfiguredBackupDirectory] = Field(default_factory=dict)

    # Timezone
    named_timezone: str = Field("Etc/UTC")

    @property
    def timezone(self) -> tzinfo:
        return dateutil.tz.gettz(self.named_timezone)

    def date_string(self, source_date: datetime) -> str:
        return source_date.astimezone(self.timezone).isoformat()


class BackupSessionConfig(BaseModel):
    client_id: UUID
    session_id: UUID
    backup_date: datetime
    started: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    allow_overwrite: bool
    description: Optional[str] = None

    class Config:
        allow_mutation = False


class BackupSession(Protocol):

    @property
    @abstractmethod
    def config(self) -> BackupSessionConfig:
        """The settings for this backup session"""

    @property
    @abstractmethod
    def server_session(self) -> "ServerSession":
        """The server session this backup session is attached to"""

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Is the session still open.  Initially True.  Will be set False when the session is completed or discarded"""

    @abstractmethod
    async def directory_def(self, definition: Directory, replaces: Optional[UUID] = None) -> DirectoryDefResponse:
        """
        Add a directory definition to the server.  The server is ultimately responsible for giving the hash of the
        :param definition: The contents of the directory with the file name as the key and the Inode as the value
        :param replaces: Overwrite an existing directory definition with this one.  This might change the id,
            so the return value must still be read
        :returns: The id of this directory on the server.
        """

    @abstractmethod
    async def upload_file_content(self, file_content: Union[FileReader, bytes], resume_id: UUID, resume_from: int = 0,
                                  is_complete: bool = True) -> Optional[str]:
        """
        Upload a file, or part of a file to the server.  The server will respond with an ID (the hash) for that file.
        If the upload is interrupted, then the backup can resume where it left off by first calling
        check_file_upload_size and then upload_file_content with the same_resume_id, sending only the remaining part of
        the file.

        Clients MUST NOT call upload_file_content in parallel or out of sequence.  This would make it impossible to
        determine how much of a request succeeded with check_file_upload_size.  Servers may raise a ProtocolError if
        this occurs.  However server authors should be mindful that their own locks could cause phantom parallel
        requests avoid tripping up a client unnecessarily.

        Clients may use the resume feature to upload non-zero sections of a partial file.  Thus servers MUST support
        the scenario where a client calls upload_file_content with a resume_from much larger than the existing partial
        file.  Even servers MUST support calling upload_file_content with resume_from > 0 on the first request for that
        file.

        Clients MUST NOT call upload_file_content on a file after it has been successfully completed (with
        complete=True).  Clients may use check_file_upload_size to check if the previous interrupted request completed.
        Here a NotFoundException would infer the previous request completed successfully.

        :param file_content: Either a Path pointing to a local file or a readable and seekable BinaryIO.  If path is
            specified then restart logic is inferred
        :param resume_id: I locally specified ID to use to resume file upload in the vent it fails part way through.
            WARNING reusing the same resume_id inside the same session will overwrite the previous file.
        :param resume_from: When resuming a failed upload, this specifies how many bytes of the partial upload to keep.
            EG: if this is set to 500 then the first 500 bytes of the partial upload will be kept and all beyond that
            will be overwritten.  Not this will implicitly cause a seek operation on file_content.
        :param is_complete: If complete is True an ID will be generated and resume_id will be invalidated.  If complete
            is False, no complete ID
        :return: The ref_hash of the newly uploaded file if complete=True or None if complete=False.  Clients may use
            ref_hash to check the file was not corrupted in transit.
        """

    @abstractmethod
    async def add_root_dir(self, root_dir_name: str, inode: Inode) -> None:
        """
        Add a root directory to the backup.  A backup consists of one or more root directory.  Attempting to complete
        a backup with no roots added will result in an error.
        :param root_dir_name: The name for this root directory
        :param inode: the stats about this backup directory including it's hash
        """

    @abstractmethod
    async def check_file_upload_size(self, resume_id: UUID) -> int:
        """
        Checks to see how much of a file was successfully uploaded.
        :param resume_id: The resume_id specified in upload_file_content
        :raises: NotFoundException if either an incorrect resume_id was specified, or otherwise the specified file
            has already completed (effectively deleting the resume_id server-side).
        """

    @abstractmethod
    async def complete(self) -> Backup:
        """
        Finalize the backup.  Once this has completed, the backup will be visible to other clients and it cannot be
        modified further.
        """

    @abstractmethod
    async def discard(self) -> None:
        """
        Delete this partial backup entirely.  This cannot be undone.  All uploads etc will be discarded from the server.
        """


class ServerSession(Protocol):

    @property
    @abstractmethod
    def client_config(self) -> ClientConfiguration:
        """
        Client confic is stored remotely on the server so that it can be centrally managed for all nodes.
        Clients read this field to discover what they should back up etc.
        """

    @abstractmethod
    async def start_backup(self, backup_date: datetime, allow_overwrite: bool = False, description: Optional[str] = None
                           ) -> BackupSession:
        """
        Create a new session on the server.  This is used to upload a backup to the server.  Backups happen as a
        transaction.  IE once a session is open, you can upload to that session, but files will not be available
        until the session has been completed.
        :param backup_date: The date/time for this backup.
            This will be rounded based on the configured backup_granularity
        :param allow_overwrite: If False then an error will be raised if the configured backup already exists.  If True
            The existing backup will be destroyed on complete().
        :param description: User specified description of this backup
        """

    @abstractmethod
    async def resume_backup(self, *, session_id: Optional[UUID] = None, backup_date: Optional[datetime] = None
                            ) -> BackupSession:
        """
        Retrieve a backup session.  It is legitimate to have multiple clients attached to the same backup session.
        However this may actually hurt performance since separate clients may end up uploading the same file each where
        a single client would only upload it once.
        :param session_id: The session id to retrieve
        :param backup_date: The backup date of the session to retrieve
        :return: The session associated with the session_id if not None otherwise the session associated with the
            backup_date
        """

    @abstractmethod
    async def list_backup_sessions(self) -> List[BackupSessionConfig]:
        """
        Fetch a list of backup sessions.  Since the list of open sessions is generally very small, this will return
        the details of each one.
        """

    @abstractmethod
    async def list_backups(self) -> List[Tuple[datetime, str]]:
        """
        Fetch list of completed backups.  Typically the number of backups can stack up very large so this only returns
        the key for each backup (the datetime) and a name.
        :return: List of backups, keyed by datetime
        """

    @abstractmethod
    async def get_backup(self, backup_date: Optional[datetime] = None) -> Optional[Backup]:
        """
        Fetch the details of a completed backup.
        :param backup_date: The backup date of the required backup.  This will be automatically normalized.  If None
            (default) the most recent backup will be retrieved.
        :return: The backup meta data or None if no backup was found.
        """

    @abstractmethod
    async def get_directory(self, inode: Inode) -> Directory:
        """
        Reads a directory
        :param inode: The handle to the directory
        """

    @abstractmethod
    async def get_file(self, inode: Inode) -> Optional[FileReader]:
        """
        Reads a file.
        :param inode: The handle to the file
        """

    async def close(self):
        """
        Release any resources
        """


class DirectoryExplorer(Protocol):

    @abstractmethod
    def iter_children(self) -> AsyncIterable[Tuple[str, Inode]]:
        """
        Gets an iterator over all the children in the directory.  Child inodes will be populated from an internal
        cache if possible, so if the same file is seen twice via different names (hard-linked) then it will return
        the same Inode object.  This is useful as it will mean previous calls to hash the file will populate the inodes
        hash.

        Otherwise expect the hash field in most files to be none to begin with.
        """

    @abstractmethod
    async def inode(self) -> Inode:
        """
        This is typically only used to get the inode for a directory root.  It fetches the inode for the base directory.
        """

    @abstractmethod
    async def open_child(self, name: str) -> FileReader:
        """
        Opens a file for async reading or writing.
        :param name: The name of the child to open.
        """

    @abstractmethod
    async def restore_child(self, name: str, type_: FileType, content: Optional[FileReader], clobber_existing: bool):
        """
        Restores a file.
        :param name: The file name of the child to restore.
        :param type_: The type of file to restore
        :param content: The file content to restore
        :param clobber_existing: If the child already exists (not as a directory)
        """

    @abstractmethod
    async def restore_meta(self, name: str, meta: Inode, toggle: Dict[str, bool]):
        """
        :param name: The name of the child to restore meta on.
        :param meta: The inode containing the meta to restore
        :param toggle: By default meta will be restored, but individual properties from the meta can be suppressed by
            setting their name=False.  Note "type", "size" and "hash" must be ignored.
        """

    @abstractmethod
    def get_child(self, name: str) -> "DirectoryExplorer":
        """
        Gets a child DirectoryExplorer connected to a child directory.  This will not verify that the child is a
        directory or even that it exists, so care must be taken on the part of the caller to ensure the name was
        previously yielded by iter_children()
        """

    def get_path(self, name: Optional[str]) -> str:
        """
        Gets a human readable name for a particular child or the parent directory
        :param name: The name of the child or None for the parent
        """


class FileSystemExplorer(Protocol):

    def __call__(self, directory_root: str, filters: Iterable[Filter] = ()) -> DirectoryExplorer:
        """
        Gets a directory explorer for the given backup root
        :param directory_root: The root specification.
        :param filters: Optional iterable of filters to ignore on search. This does not affect restoring.
        :returns: A DirectoryExplorer pointing to the root path with the given filters embedded.
        """


class RequestException(Exception):
    http_status = 400  # Not knowing the cause of this request exception we can only assume it was an internal error


class AccessDeniedException(RequestException):
    http_status = 403


class NotFoundException(RequestException):
    http_status = 404  # Not Found


class InternalServerError(RequestException):
    http_status = 500  # Server did something wong.  Check the server logs.


class SessionClosed(RequestException):
    http_status = 410  # Gone


class DuplicateBackup(RequestException):
    http_status = 409 # Conflict


class ProtocolError(Exception):
    http_status: int = 400  # Bad request


class InvalidArgumentsError(ProtocolError, ValueError):
    http_status: int = 422  # Unprocessable entity


class InvalidResponseError(ProtocolError):
    http_status: int = 502  # Bad response from backend


# Remote server-client interaction needs a way for the server to raise an exception with the client. Obviously we don't
# want to give the server free reign to raise any exception so anything in this module (or imported into it) can be
# raised by the server by name.
EXCEPTIONS_BY_NAME = {
    name: ex for name, ex in globals().items() if isinstance(ex, type) and issubclass(ex, Exception)
}

EXCEPTIONS_BY_TYPE = {
    ex: name for name, ex in globals().items() if isinstance(ex, type) and issubclass(ex, Exception)
}


class RemoteException(BaseModel):
    name: str
    message: str

    #pylint: disable=no-self-argument,no-self-use
    @validator('name')
    def _name_in_exceptions_by_name(cls, name: str) -> str:
        if name not in EXCEPTIONS_BY_NAME:
            raise ValueError(f"Invalid exception name: {name}", RemoteException)
        return name

    @classmethod
    def from_exception(cls, exception: Union[ProtocolError, RequestException]) -> "RemoteException":
        return cls(name=EXCEPTIONS_BY_TYPE[type(exception)], message=str(exception))

    def exception(self) -> Union[RequestException, ProtocolError]:
        exception = EXCEPTIONS_BY_NAME[self.name]
        return exception(self.message)


def normalize_backup_date(backup_date: datetime, backup_granularity: timedelta, client_timezone: tzinfo):
    """
    Normalize a backup date to the given granularity. EG: if granularity is set to 1 day, the backup_date is set to
    midnight of that same day.  If granularity is set to 1 hour, then backup_date is set to the start of that hour.
    """
    assert backup_date.tzinfo is not None
    timestamp = backup_date.timestamp()
    timestamp -= timestamp % backup_granularity.total_seconds()
    return datetime.fromtimestamp(timestamp, client_timezone)


HashType = hashlib.sha256


@functools.singledispatch
def hash_content(content: bytes) -> str:
    """
    Generate an sha256sum for the given content.
    """
    hash_object = HashType()
    hash_object.update(content)
    return hash_object.hexdigest()


@hash_content.register
def _(content: str) -> str:
    """
    Generate an sha256sum for the given content.
    """
    return hash_content(content.encode("utf-8"))


async def async_hash_content(content: FileReader):
    """
    Generate an sha256sum for the given content.  Yes this is absolutely part of the protocol!
    Either the server or client can hash the same file and the result MUST match on both sides or things will break.
    """
    hash_object = HashType()
    bytes_read = await content.read(READ_SIZE)
    while bytes_read:
        hash_object.update(bytes_read)
        bytes_read = await content.read(READ_SIZE)
    return hash_object.hexdigest()
