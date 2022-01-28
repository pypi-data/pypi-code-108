# pylint: disable=protected-access
import hashlib
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union, List, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel

from . import protocol
from .local_file_system import AsyncFile, async_stat
from .protocol import Inode, Directory, Backup, BackupSessionConfig

_CONFIG_FILE = 'config.json'


logger = logging.getLogger(__name__)


class Configuration(BaseModel):
    store_split_count = 1
    store_split_size = 2


class LocalDatabase:
    config: Configuration

    _CLIENT_DIR = 'client'
    _STORE_DIR = 'store'

    def __init__(self, base_path: Path):
        self._base_path = base_path
        self.config = Configuration.parse_file(base_path / _CONFIG_FILE)

    @property
    def path(self) -> Path:
        return self._base_path

    def save_config(self):
        with (self._base_path / _CONFIG_FILE).open('w') as file:
            file.write(self.config.json(indent=True))

    def open_client_session(self, client_id_or_name: str) -> "LocalDatabaseServerSession":
        try:
            try:
                client_id = UUID(client_id_or_name)
                client_path = self._base_path / self._CLIENT_DIR / str(client_id)
            except ValueError:
                client_path = self._base_path / self._CLIENT_DIR / client_id_or_name
                if client_path.is_symlink():
                    client_id = os.readlink(client_path)
                    client_path = self._base_path / self._CLIENT_DIR / client_id
            return LocalDatabaseServerSession(self, client_path)
        except FileNotFoundError as exc:
            logger.error(f"Session not found {client_id_or_name}")
            raise protocol.SessionClosed(f"No such session {client_id_or_name}") from exc

    def store_path_for(self, ref_hash: str) -> Path:
        split_size = self.config.store_split_size
        split_count = self.config.store_split_count
        split = [ref_hash[x:x+split_size] for x in range(0, split_count * split_size, split_size)]
        return self._base_path.joinpath(self._STORE_DIR, *split, ref_hash)

    def create_client(self, client_config: protocol.ClientConfiguration) -> protocol.ServerSession:
        (self._base_path / self._CLIENT_DIR).mkdir(exist_ok=True, parents=True)
        client_name_path = self._base_path / self._CLIENT_DIR / client_config.client_name
        client_name_path.symlink_to(str(client_config.client_id))
        client_path = self._base_path / self._CLIENT_DIR / str(client_config.client_id)
        client_path.mkdir(exist_ok=False, parents=True)
        with (client_path / _CONFIG_FILE).open('w') as file:
            file.write(client_config.json(indent=True))
        return LocalDatabaseServerSession(self, client_path)

    @classmethod
    def create_database(cls, base_path: Path, configuration: Configuration) -> "LocalDatabase":
        base_path.mkdir(exist_ok=False, parents=True)
        with (base_path / _CONFIG_FILE).open('w') as file:
            file.write(configuration.json(indent=True))
        (base_path / cls._STORE_DIR).mkdir(exist_ok=False, parents=True)
        (base_path / cls._CLIENT_DIR).mkdir(exist_ok=False, parents=True)
        return cls(base_path)


class LocalDatabaseServerSession(protocol.ServerSession):

    _BACKUPS = 'backup'
    _SESSIONS = 'sessions'
    _TIMESTMAP_FORMAT = "%Y-%m-%d_%H:%M:%S.%f"
    _DIR_SUFFIX = ".d"

    client_config: protocol.ClientConfiguration = None

    def __init__(self, database: LocalDatabase, client_path: Path):
        self._database = database
        self._client_path = client_path
        with (client_path / _CONFIG_FILE).open('r') as file:
            self.client_config = protocol.ClientConfiguration.parse_raw(file.read())

    def save_config(self):
        with (self._client_path / _CONFIG_FILE).open('w') as file:
            file.write(self.client_config.json(indent=True))

    async def start_backup(self, backup_date: datetime, allow_overwrite: bool = False,
                           description: Optional[str] = None) -> protocol.BackupSession:
        backup_date = protocol.normalize_backup_date(backup_date, self.client_config.backup_granularity,
                                                     self.client_config.timezone)

        if not allow_overwrite:
            # TODO consider raising the same exception if an open session already exists for the same date
            if self._path_for_backup_date(backup_date).exists():
                raise protocol.DuplicateBackup(f"Backup exists {backup_date.isoformat()}")

        backup_session_id = uuid4()
        backup_session_path = self._path_for_session_id(backup_session_id)
        backup_session_path.mkdir(exist_ok=False, parents=True)
        session_config = protocol.BackupSessionConfig(
            client_id=self.client_config.client_id,
            session_id=backup_session_id,
            allow_overwrite=allow_overwrite,
            backup_date=backup_date,
            description=description,
        )
        with (backup_session_path / _CONFIG_FILE).open('w') as file:
            file.write(session_config.json(indent=True))

        return LocalDatabaseBackupSession(self, backup_session_path)

    async def resume_backup(self, *, session_id: Optional[UUID] = None,
                            backup_date: Optional[datetime] = None) -> protocol.BackupSession:
        if session_id is not None:
            backup_path = self._path_for_session_id(session_id)
            return LocalDatabaseBackupSession(self, backup_path)

        if backup_date is not None:
            # This is inefficient if there are a lot of sessions but it get's the job done.
            backup_date = protocol.normalize_backup_date(backup_date, self.client_config.backup_granularity,
                                                         self.client_config.timezone)
            for session_path in (self._client_path / self._SESSIONS).iterdir():
                session = LocalDatabaseBackupSession(self, session_path)
                if session.config.backup_date == backup_date:
                    return session

            raise protocol.NotFoundException(f"Backup date not found {backup_date}")

        raise ValueError("Either session_id or backup_date must be specified but neither were")

    async def list_backup_sessions(self) -> List[protocol.BackupSessionConfig]:
        results = []
        for backup in (self._client_path / self._SESSIONS).iterdir():
            with (backup / _CONFIG_FILE).open('r') as file:
                backup_config = protocol.BackupSessionConfig.parse_raw(file.read())
            results.append(backup_config)
        return results


    async def list_backups(self) -> List[Tuple[datetime, str]]:
        results = []
        for backup in (self._client_path / self._BACKUPS).iterdir():
            with backup.open('r') as file:
                backup_config = protocol.Backup.parse_raw(file.read())
            results.append((backup_config.backup_date, backup_config.description))
        return results

    async def get_backup(self, backup_date: Optional[datetime] = None) -> Optional[Backup]:
        if backup_date is None:
            try:
                backup_path = next(iter(sorted((self._client_path / self._BACKUPS).iterdir(), reverse=True)))
            except (FileNotFoundError, StopIteration):
                logger.warning(f"No backup found for {self.client_config.client_name} ({self.client_config.client_id})")
                return None
        else:
            backup_date = protocol.normalize_backup_date(backup_date, self.client_config.backup_granularity,
                                                         self.client_config.timezone)
            backup_path = self._path_for_backup_date(backup_date)
        with backup_path.open('r') as file:
            return protocol.Backup.parse_raw(file.read())

    async def get_directory(self, inode: Inode) -> Directory:
        if inode.type != protocol.FileType.DIRECTORY:
            raise ValueError(f"Cannot open file type {inode.type} as a directory")
        inode_hash = inode.hash + self._DIR_SUFFIX
        with self._database.store_path_for(inode_hash).open('r') as file:
            return Directory.parse_raw(file.read())

    async def get_file(self, inode: Inode) -> Optional[protocol.FileReader]:
        if inode.type not in (protocol.FileType.REGULAR, protocol.FileType.LINK, protocol.FileType.PIPE):
            raise ValueError(f"Cannot read a file type {inode.type}")
        result_path = self._database.store_path_for(inode.hash)
        return await AsyncFile.open(result_path, "r")

    def complete_backup(self, meta: protocol.Backup, overwrite: bool):
        backup_path = self._path_for_backup_date(meta.backup_date)
        backup_path.parent.mkdir(exist_ok=True, parents=True)
        with backup_path.open('w' if overwrite else 'x') as file:
            file.write(meta.json(indent=True))

    def _path_for_backup_date(self, backup_date: datetime) -> Path:
        return self._client_path / self._BACKUPS / (backup_date.strftime(self._TIMESTMAP_FORMAT) + '.json')

    def _path_for_session_id(self, session_id: UUID) -> Path:
        return self._client_path / self._SESSIONS / str(session_id)


class LocalDatabaseBackupSession(protocol.BackupSession):

    _PARTIAL = 'partial'
    _NEW_OBJECTS = 'new_objects'
    _ROOTS = 'roots'

    def __init__(self, client_session: LocalDatabaseServerSession, session_path: Path):
        self._server_session = client_session
        self._session_path = session_path
        try:
            with (session_path / _CONFIG_FILE).open('r') as file:
                self._config = protocol.BackupSessionConfig.parse_raw(file.read())
        except FileNotFoundError as exc:
            raise protocol.SessionClosed(session_path.name) from exc
        (session_path / self._NEW_OBJECTS).mkdir(exist_ok=True, parents=True)
        (session_path / self._ROOTS).mkdir(exist_ok=True, parents=True)
        (session_path / self._PARTIAL).mkdir(exist_ok=True, parents=True)

    @property
    def config(self) -> BackupSessionConfig:
        return self._config

    async def directory_def(self, definition: protocol.Directory, replaces: Optional[UUID] = None
                            ) -> protocol.DirectoryDefResponse:
        if not self.is_open:
            raise protocol.SessionClosed()
        for name, child in definition.children.items():
            if child.hash is None:
                raise protocol.InvalidArgumentsError(f"Child {name} has no hash value")

        directory_hash, content = definition.hash()
        if self._object_exists(directory_hash + self._server_session._DIR_SUFFIX):
            logger.debug(f"Directory def already exists {directory_hash}")
            return protocol.DirectoryDefResponse(ref_hash=directory_hash)

        missing = []
        for name, inode in definition.children.items():
            inode_hash = inode.hash
            if inode.type is protocol.FileType.DIRECTORY:
                inode_hash += self._server_session._DIR_SUFFIX
            if not self._object_exists(inode_hash):
                missing.append(name)

        if missing:
            logger.debug(f"Directory def missing {len(missing)} items in store")
            return protocol.DirectoryDefResponse(missing_files=missing)

        tmp_path = self._temp_path()
        with tmp_path.open('xb') as file:
            try:
                file.write(content)
                tmp_path.rename(self._store_path_for(directory_hash + self._server_session._DIR_SUFFIX))
            except:
                tmp_path.unlink()
                raise

        # Success
        logger.debug(f"Directory def created {directory_hash}")
        return protocol.DirectoryDefResponse(ref_hash=directory_hash)

    async def upload_file_content(self, file_content: Union[protocol.FileReader, bytes], resume_id: UUID,
                                  resume_from: int = 0, is_complete: bool = True) -> Optional[str]:
        if not self.is_open:
            raise protocol.SessionClosed()
        hash_object = hashlib.sha256()
        temp_file = self._temp_path(resume_id)
        complete_partial = is_complete and resume_from > 0
        temp_file.touch()
        with await AsyncFile.open(temp_file, 'r+') as target:
            # If we are completing the file we must hash it.
            if complete_partial:
                logger.debug(f"Completing file; re-reading partial for {resume_id}")
                # TODO sanity check the request to ensure complete_partial always writes to the end of the file
                target.seek(0, os.SEEK_SET)
                while target.tell() < resume_from:
                    bytes_read = await target.read(min(protocol.READ_SIZE, resume_from - target.tell()))
                    if not bytes_read:
                        # TODO prevent memory DOS attack. Limit the chunks this can be fed in for.
                        bytes_read = bytes(resume_from - target.tell())
                        target.seek(resume_from, os.SEEK_SET)
                    hash_object.update(bytes_read)
                assert target.tell() == resume_from
            # If not complete then we just seek to the requested resume_from position
            else:
                target.seek(resume_from, os.SEEK_SET)

            # Write the file content
            if isinstance(file_content, bytes):
                if is_complete:
                    hash_object.update(file_content)
                await target.write(file_content)
            else:
                bytes_read = await file_content.read(protocol.READ_SIZE)
                while bytes_read:
                    if is_complete:
                        hash_object.update(bytes_read)
                    await target.write(bytes_read)
                    bytes_read = await file_content.read(protocol.READ_SIZE)

        if not is_complete:
            return None

        # Move the temporary file to new_objects named as it's hash
        # For this purpose we can assume it's a regular file.  As long as it's not a directory that's all okay.
        ref_hash = hash_object.hexdigest()
        if self._object_exists(ref_hash):
            logger.warning(f"File already exists after upload {resume_id} as {ref_hash}")
            temp_file.unlink()
        else:
            logger.debug(f"File upload complete {resume_id} as {ref_hash}")
            temp_file.rename(self._new_object_path_for(ref_hash))
        return ref_hash

    async def add_root_dir(self, root_dir_name: str, inode: protocol.Inode) -> None:
        if not self.is_open:
            raise protocol.SessionClosed()
        location_hash = inode.hash
        if inode.type is protocol.FileType.DIRECTORY:
            location_hash += self._server_session._DIR_SUFFIX
        if not self._object_exists(location_hash):
            raise ValueError(f"Cannot create {root_dir_name} - does not exist: {inode.hash}")
        file_path = self._session_path / self._ROOTS / root_dir_name
        with file_path.open('x') as file:
            file.write(inode.json())

    async def check_file_upload_size(self, resume_id: UUID) -> int:
        if not self.is_open:
            raise protocol.SessionClosed()
        return (await async_stat(self._temp_path(resume_id))).st_size

    async def complete(self) -> protocol.Backup:
        if not self.is_open:
            raise protocol.SessionClosed()
        logger.info(f"Committing {self._session_path.name} for {self._server_session.client_config.client_name} "
                    f"({self._server_session.client_config.client_id}) - {self._config.backup_date}")
        for file_path in (self._session_path / self._NEW_OBJECTS).iterdir():
            try:
                target_path = self._server_session._database.store_path_for(file_path.name)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Moving {file_path.name} to store")
                file_path.rename(target_path)
            except FileExistsError:
                # This should be rare.  To happen two concurrent backup sessions must try to add the same new file.
                logger.warning(f"Another session has already uploaded {file_path.name}... skipping file.")
        roots = {}
        for file_path in (self._session_path / self._ROOTS).iterdir():
            with file_path.open('r') as file:
                roots[file_path.name] = protocol.Inode.parse_raw(file.read())
        backup_meta = protocol.Backup(
            client_id=self._server_session.client_config.client_id,
            client_name=self._server_session.client_config.client_name,
            backup_date=self._config.backup_date,
            started=self._config.started,
            completed=datetime.now(timezone.utc),
            description=self._config.description,
            roots=roots,
        )
        self._server_session.complete_backup(backup_meta, self._config.allow_overwrite)
        await self.discard()
        return backup_meta

    async def discard(self) -> None:
        if not self.is_open:
            raise protocol.SessionClosed()
        shutil.rmtree(self._session_path)

    def _object_exists(self, ref_hash: str) -> bool:
        return (self._server_session._database.store_path_for(ref_hash).exists()
                or self._store_path_for(ref_hash).exists())

    def _store_path_for(self, ref_hash: str) -> Path:
        return self._session_path / self._NEW_OBJECTS / ref_hash

    def _temp_path(self, resume_id: Optional[UUID] = None) -> Path:
        if resume_id is None:
            resume_id = uuid4()
        return self._session_path / self._PARTIAL / str(resume_id)

    def _new_object_path_for(self, ref_hash: str) -> Path:
        return self._session_path / self._NEW_OBJECTS / ref_hash

    @property
    def server_session(self) -> protocol.ServerSession:
        return self._server_session

    @property
    def is_open(self) -> bool:
        return self._session_path.exists()
