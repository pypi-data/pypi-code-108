import abc
import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from os import SEEK_SET, SEEK_END
from pathlib import Path
from typing import Optional, BinaryIO, Union, Protocol, Any, Dict, List, Tuple
from uuid import UUID
import json
import logging

import requests.auth

from . import protocol, http_protocol
from .protocol import Inode, Directory, DirectoryDefResponse, Backup, BackupSession, ClientConfiguration, \
    BackupSessionConfig


logger = logging.getLogger(__name__)


class Client(Protocol):

    @abc.abstractmethod
    async def request(self, endpoint: http_protocol.Endpoint, body = None, **params: Any):
        """
        Send request to server for a specific response.
        :param endpoint: A specification of of the URL, parameters and return type
        :param body: Optional object to send in the body. Can be anything requests can handle
        :param params: Keyword arguments which will be formed into the URL and query
        """

    @abc.abstractmethod
    def close(self):
        """
        Cleanup all resources for this client (eg: open connections and worker threads)
        """

    def __enter__(self):
        """
        Context manager does nothing special on open
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Must close self
        """
        self.close()


class ClientSession(protocol.ServerSession):

    def __init__(self, client: Client, client_config: http_protocol.USER_CLIENT_CONFIG):
        self._client = client
        self._client_config = client_config

    @classmethod
    async def create_session(cls, client: Client) -> "ClientSession":
        client_config = await client.request(http_protocol.USER_CLIENT_CONFIG)
        return cls(client=client, client_config=client_config)

    @property
    def client_config(self) -> ClientConfiguration:
        return self._client_config

    async def list_backup_sessions(self) -> List[BackupSessionConfig]:
        # TODO
        raise NotImplementedError()

    async def list_backups(self) -> List[Tuple[datetime, str]]:
        all_backups: http_protocol.ListBackup = await self._client.request(http_protocol.LIST_BACKUPS)
        return [(backup.backup_date, backup.description) for backup in all_backups.__root__]

    async def start_backup(self, backup_date: datetime, allow_overwrite: bool = False,
                           description: Optional[str] = None) -> BackupSession:
        return ClientBackupSession(self, await self._client.request(
            endpoint=http_protocol.START_BACKUP,
            backup_date=backup_date,
            allow_overwrite=allow_overwrite,
            description=description
        ))

    async def resume_backup(self, *, session_id: Optional[UUID] = None,
                            backup_date: Optional[datetime] = None) -> BackupSession:
        return ClientBackupSession(self, await self._client.request(
            endpoint=http_protocol.RESUME_BACKUP,
            session_id=session_id,
            backup_date=backup_date
        ))

    async def get_backup(self, backup_date: Optional[datetime] = None) -> Optional[Backup]:
        if backup_date is None:
            return await self._client.request(http_protocol.BACKUP_LATEST)
        return await self._client.request(http_protocol.BACKUP_BY_DATE, backup_date=backup_date)

    async def get_directory(self, inode: Inode) -> Directory:
        if inode.type != protocol.FileType.DIRECTORY:
            raise protocol.InvalidArgumentsError("Inode is not a directory")
        result = await self._client.request(http_protocol.GET_DIRECTORY, ref_hash=inode.hash)
        return Directory(__root__=result.children)

    async def get_file(self, inode: Inode) -> Optional[protocol.FileReader]:
        if inode.type is protocol.FileType.DIRECTORY:
            raise protocol.InvalidArgumentsError(f'Cannot get file of type {inode.type}')
        result = await self._client.request(http_protocol.GET_FILE, ref_hash=inode.hash)
        return result


class ClientBackupSession(protocol.BackupSession):

    def __init__(self, client_session: ClientSession, config: BackupSessionConfig):
        self._client_session = client_session
        self._config = config
        self._client = client_session._client

    @property
    def config(self) -> BackupSessionConfig:
        return self._config

    @property
    def server_session(self) -> ClientSession:
        return self._client_session

    @property
    def is_open(self) -> bool:
        # TODO figure out how to do this
        return True

    async def _request(self, endpoint: http_protocol.Endpoint, body = None, **params: Any):
        return await self._client.request(endpoint, body, session_id=self._config.session_id, **params)

    async def directory_def(self, definition: Directory, replaces: Optional[UUID] = None) -> DirectoryDefResponse:
        result: DirectoryDefResponse = await self._request(
            endpoint=http_protocol.DIRECTORY_DEF,
            body=definition,
            replaces=replaces,
        )
        if result.success:
            assert result.missing_ref is None
            # TODO consider adding ref_hash into DirectoryDefResponse
            # assert result.ref_hash is not None
        return result

    async def upload_file_content(self, file_content: Union[protocol.FileReader, bytes], resume_id: UUID,
                                  resume_from: int = 0, is_complete: bool = True) -> Optional[str]:
        if isinstance(file_content, bytes):
            return await self._request(
                endpoint=http_protocol.UPLOAD_FILE,
                body=file_content,
                resume_id=resume_id,
                resume_from=resume_from,
                is_complete=is_complete
            )

        # TODO detect sparse files and upload in chunks
        position = resume_from
        total_size = file_content.file_size
        bytes_read = await file_content.read(protocol.READ_SIZE)
        while bytes_read:
            new_position = position + len(bytes_read)
            ref_hash = await self._request(
                endpoint=http_protocol.UPLOAD_FILE,
                body=bytes_read,
                resume_id=resume_id,
                resume_from=position,
                is_complete=is_complete if new_position == total_size else False
            )
            if new_position == total_size:
                return ref_hash
            position = new_position
            bytes_read = await file_content.read(protocol.READ_SIZE)
        if is_complete:
            logger.warning(f"Expected to upload {file_content.file_size} but only managed {position} before EOF. "
                           f"Perhaps the file changed.")
            return await self._request(
                endpoint=http_protocol.UPLOAD_FILE,
                body=bytes(),
                resume_id=resume_id,
                position=position,
                is_complete=True,
            )
        # Here we have reached the end of the content and we do not need to mark the file as complete
        return None


    async def add_root_dir(self, root_dir_name: str, inode: Inode) -> None:
        await self._request(http_protocol.ADD_ROOT_DIR, body=inode, root_dir_name=root_dir_name)

    async def check_file_upload_size(self, resume_id: UUID) -> int:
        response = await self._request(http_protocol.FILE_PARTIAL_SIZE, resume_id=resume_id)
        return response.size

    async def complete(self) -> Backup:
        return await self._request(http_protocol.COMPLETE_BACKUP)

    async def discard(self) -> None:
        return await self._request(http_protocol.DISCARD_BACKUP)


class RequestsClient(Client):
    _base_url: str
    _server_version: http_protocol.ServerVersion
    _executor: Executor
    _http_session: requests.Session

    def __init__(self, server: http_protocol.ServerProperties):
        server_path = server.copy()
        server_path.credentials = None
        self._base_url = server_path.format_url()
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._http_session = requests.Session()

    async def request(self, endpoint: http_protocol.Endpoint, body = None, **params: Any) -> Any:
        return await asyncio.get_running_loop().run_in_executor(
            self._executor, self._request_object, endpoint, params, body)

    async def server_version(self) -> http_protocol.ServerVersion:
        return await self.request(http_protocol.HELLO)

    def _request_object(self, endpoint: http_protocol.Endpoint, params: Dict[str, Any], body = None):
        response = self._send_request(endpoint, params, body)
        return self._parse_response(endpoint, response)

    def _send_request(self,  endpoint: http_protocol.Endpoint, params: Dict[str, Any],
                      body = None) -> requests.Response:
        url = endpoint.format_url(self._base_url, params)
        stream_response = isinstance(endpoint.result_type, BinaryIO)

        if body is None:
            response = self._send_raw_request(endpoint.method, url, stream_response)
        elif isinstance(body, bytes):
            response = self._send_raw_request(endpoint.method, url, stream_response, files={'file': body})
        elif hasattr(body, 'json'):
            response = self._send_raw_request(endpoint.method, url, stream_response, data=body.json().encode(),
                                          headers={'Content-Type': 'application/json'})
        else:
            raise protocol.InvalidArgumentsError(f"Cannot send body type {type(body).__name__}")
        self._check_response(response)
        return response

    def _send_raw_request(self, method: str, url: str, stream_response: bool, **kwargs) -> requests.Response:
        return self._http_session.request(method, url, stream=stream_response, **kwargs)

    @staticmethod
    def _check_response(response: requests.Response):
        if response.status_code >= 400:
            status_code = response.status_code
            content = response.content
            response.close()
            try:
                # Try to parse this as a remote exception.
                remote_exception = protocol.RemoteException.parse_raw(content)
            except ValueError:
                pass
            else:
                # If this was a valid remote exception we can just raise it.
                raise remote_exception.exception() from None

            try:
                message = "\n" + content.decode()
            except UnicodeDecodeError:
                message = ""
            if status_code == 422:
                raise protocol.InvalidArgumentsError(message)
            raise protocol.InvalidResponseError(f"Bad response from server {status_code}: {message}")

    def _parse_response(self, endpoint: http_protocol.Endpoint, server_response: requests.Response):
        if endpoint.result_type is protocol.FileReader:
            try:
                return RequestResponse(server_response, self._executor)
            except:
                # Closing the RequestResponse will close the server_response. But if we fail to creat one, we must
                # close ourselves.
                server_response.close()
                raise
        try:
            if endpoint.result_type is None:
                return None
            result = json.loads(server_response.content)
            if result is not None and hasattr(endpoint.result_type, 'parse_obj'):
                return endpoint.result_type.parse_obj(result)
            return result

        finally:
            # If we need to close the result, it might not be a good idea to close without reading the content
            # This results in closing the connection which may slow down future requests.  If the Content-Length
            # header shows less than 10KB, we read the content and leave the connection open by consuming the body.
            # This has not been performance tuned: 10KB is a guess.
            try:
                if int(server_response.headers['Content-Length']) <= 10240:
                    _ = server_response.content

            # pylint: disable=broad-except
            # Honestly we really don't care if / why the above failed.  except Exception will not cat keyboard
            # interrupt etc.  But pretty much any socket error, or the Content-Length missing from the response
            # Can and should be handled by simply closing the response as we'd intended to do anyway.
            except Exception:
                pass
            server_response.close()

    def close(self):
        self._executor.shutdown(wait=False)
        self._http_session.close()


class RequestResponse(protocol.FileReader):
    def __init__(self, response: requests.Response, executor: Executor):
        self._response = response
        self._content = self._response.iter_content(protocol.READ_SIZE)
        self._cached_content = BytesIO()
        self._executor = executor

    async def read(self, num_bytes: int = -1) -> bytes:
        if num_bytes < 0:
            return await asyncio.get_running_loop().run_in_executor(self._executor, self._read_all)
        return await asyncio.get_running_loop().run_in_executor(self._executor, self._read_partial, num_bytes)

    def _read_all(self) -> bytes:
        current_pos = self._cached_content.tell()
        self._cached_content.seek(0, SEEK_END)
        for block in self._content:
            self._cached_content.write(block)
        self._cached_content.seek(current_pos, SEEK_SET)
        return self._cached_content.read(self._cached_content.getbuffer().nbytes - current_pos)

    def _read_partial(self, num_bytes: int) -> bytes:
        result = self._cached_content.read(num_bytes)
        if not result:
            try:
                self._cached_content = BytesIO(next(self._content))
            except StopIteration:
                return bytes()
            result = self._cached_content.read(num_bytes)
        return result

    def close(self):
        self._response.close()

    @property
    def file_size(self) -> Optional[int]:
        try:
            return int(self._response.headers['Content-Length'])
        except KeyError:
            return None
