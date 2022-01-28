import functools
import logging
from datetime import datetime, timezone
from typing import Optional, Union, Callable, Awaitable
from uuid import UUID

import asyncstdlib
import fastapi.responses

from . import SERVER_VERSION, security
from .. import protocol, http_protocol, misc
from ..local_database import LocalDatabase


logger = logging.getLogger(__name__)


def configure(authorizer: Optional[Callable[[fastapi.Request], Awaitable[security.SimpleAuthorization]]],
              local_database: LocalDatabase):
    # pylint: disable=invalid-name
    global _authorizer, _local_database
    _authorizer = authorizer
    _local_database = local_database


# pylint: disable=invalid-name
_authorizer: Optional[Callable[[fastapi.Request], Awaitable[security.SimpleAuthorization]]] = None
_local_database: Optional[LocalDatabase] = None


app = fastapi.FastAPI()

METHOD_MAP = {
    'GET': app.get,
    'POST': app.post,
    'PUT': app.put,
    'DELETE': app.delete,
}


def endpoint(spec: http_protocol.Endpoint, **kwargs):
    """
    Attach the method to the app at the given endpoint
    Annotation which evaluates to get, post, put, delete with a URL stub and response model.
    """
    if spec.result_type is None or spec.result_type == protocol.FileReader:
        annotation = METHOD_MAP[spec.method](path=spec.url_stub, **kwargs)
    else:
        annotation = METHOD_MAP[spec.method](path=spec.url_stub, response_model=spec.result_type)
    return annotation


async def authorize(request: fastapi.Request) -> security.SimpleAuthorization:
    return await _authorizer(request)


def user_session(credentials=fastapi.Depends(authorize)) -> protocol.ServerSession:
    session = _cached_server_session(client_id_or_name=security.get_client_id(credentials))
    return session


async def backup_session(session_id: UUID, credentials=fastapi.Depends(authorize)):
    return await _cached_backup_session(client_id_or_name=security.get_client_id(credentials),
                                        backup_session_id=session_id)


# TODO find a way to make 128 configurable
@functools.lru_cache(maxsize=128)
def _cached_server_session(client_id_or_name: str) -> protocol.ServerSession:
    return _local_database.open_client_session(client_id_or_name=client_id_or_name)


# TODO find a way to make 128 configurable
@asyncstdlib.lru_cache(maxsize=128)
async def _cached_backup_session(client_id_or_name: str, backup_session_id: UUID) -> protocol.BackupSession:
    server_session = _cached_server_session(client_id_or_name=client_id_or_name)
    return await server_session.resume_backup(session_id=backup_session_id)


@endpoint(http_protocol.HELLO)
async def hello() -> http_protocol.ServerVersion:
    return SERVER_VERSION


@endpoint(http_protocol.USER_CLIENT_CONFIG)
async def about_me(session: protocol.ServerSession = fastapi.Depends(user_session)) -> protocol.ClientConfiguration:
    # Force a cache refresh when the client asks for their settings.
    clear_cache()
    # Fetch the client session a second time, but this time with an empty cache, reloading the client_config from disk.
    session = _cached_server_session(str(session.client_config.client_id))
    return session.client_config


@endpoint(http_protocol.LIST_BACKUPS)
async def list_backups(session: protocol.ServerSession = fastapi.Depends(user_session)) -> http_protocol.LIST_BACKUPS:
    all_backups = await session.list_backups()
    descriptions = [http_protocol.BackupDescription(backup_date=backup_date, description=description)
                    for backup_date, description in all_backups]
    return http_protocol.ListBackup(__root__=descriptions)


@endpoint(http_protocol.BACKUP_LATEST)
async def get_backup_latest(session: protocol.ServerSession = fastapi.Depends(user_session)) -> protocol.Backup:
    return await session.get_backup(backup_date=None)


@endpoint(http_protocol.BACKUP_BY_DATE)
async def get_backup_by_date(backup_date: datetime,
                             session: protocol.ServerSession = fastapi.Depends(user_session)
                             ) -> protocol.Backup:
    return await session.get_backup(backup_date=backup_date)


@endpoint(http_protocol.GET_DIRECTORY)
async def get_directory(ref_hash: str,
                        session: protocol.ServerSession = fastapi.Depends(user_session)
                        ) -> http_protocol.GetDirectoryResponse:
    inode = protocol.Inode(mode=0, size=0, uid=0, gid=0, hash=ref_hash, type=protocol.FileType.DIRECTORY,
                           modified_time=datetime(year=1970, month=1, day=1))
    result =  await session.get_directory(inode=inode)
    return http_protocol.GetDirectoryResponse(children=result.children)


@endpoint(http_protocol.GET_FILE)
async def get_file(ref_hash: str, session: protocol.ServerSession = fastapi.Depends(user_session)) -> fastapi.Response:
    read_size = 1024*1024
    async def read_content():
        with content:
            bytes_read = await content.read(read_size)
            while bytes_read:
                yield bytes_read
                bytes_read = await content.read(read_size)

    inode = protocol.Inode(mode=0, size=0, uid=0, gid=0, hash=ref_hash, type=protocol.FileType.REGULAR,
                           modified_time=datetime(year=1970, month=1, day=1))
    content = await session.get_file(inode)

    try:
        if content.file_size is not None:
            headers = {'Content-Length': str(content.file_size)}
        else:
            headers = {}
        return fastapi.responses.StreamingResponse(content=read_content(), status_code=200, headers=headers)
    except:
        content.close()
        raise


@endpoint(http_protocol.START_BACKUP)
async def start_backup(session: protocol.ServerSession = fastapi.Depends(user_session),
                       backup_date: Optional[datetime] = None, allow_overwrite: bool = False,
                       description: Optional[str] = None) -> protocol.BackupSessionConfig:
    if backup_date is None:
        backup_date = datetime.now(timezone.utc)
    return (await session.start_backup(
        backup_date=backup_date,
        allow_overwrite=allow_overwrite,
        description=description,
    )).config


@endpoint(http_protocol.RESUME_BACKUP)
async def resume_backup(session: protocol.ServerSession = fastapi.Depends(user_session), session_id: UUID = None,
                        backup_date: datetime = None) -> protocol.BackupSessionConfig:
    session = await session.resume_backup(session_id=session_id, backup_date=backup_date)
    return session.config


@endpoint(http_protocol.DISCARD_BACKUP)
async def discard_backup(session: protocol.BackupSession = fastapi.Depends(backup_session)) -> fastapi.Response:
    await session.discard()
    return fastapi.Response(status_code=204)


@endpoint(http_protocol.COMPLETE_BACKUP)
async def complete_backup(session: protocol.BackupSession = fastapi.Depends(backup_session)) -> protocol.Backup:
    return await session.complete()


@endpoint(http_protocol.DIRECTORY_DEF)
async def directory_definition(definition: protocol.Directory, replaces: Optional[UUID] = None,
                               session: protocol.BackupSession = fastapi.Depends(backup_session)
                               ) -> protocol.DirectoryDefResponse:
    return await session.directory_def(definition=definition, replaces=replaces)


@endpoint(http_protocol.UPLOAD_FILE)
async def upload_file_content(resume_id: UUID, file: fastapi.UploadFile = fastapi.File(...),
                              session: protocol.BackupSession = fastapi.Depends(backup_session),
                              resume_from: int = 0, is_complete: bool = True) -> str:
    return await session.upload_file_content(
        file_content=file,
        resume_id=resume_id,
        resume_from=resume_from,
        is_complete=is_complete,
    )


@endpoint(http_protocol.FILE_PARTIAL_SIZE)
async def file_partial_size(resume_id: UUID, session: protocol.BackupSession = fastapi.Depends(backup_session)) -> int:
    return await session.check_file_upload_size(resume_id=resume_id)


@endpoint(http_protocol.ADD_ROOT_DIR)
async def add_root_directory(root_dir_name: str, inode: protocol.Inode,
                             session: protocol.BackupSession = fastapi.Depends(backup_session)):
    await session.add_root_dir(root_dir_name=root_dir_name, inode=inode)
    return fastapi.Response(status_code=204)


@app.exception_handler(protocol.RequestException)
@app.exception_handler(protocol.ProtocolError)
def exception_handler(_: fastapi.Request, exc: Union[protocol.ProtocolError, protocol.RequestException]
                      ) -> fastapi.responses.JSONResponse:
    # Only print stack trace on protocol exception
    logger.error(misc.str_exception(exc), exc_info=isinstance(exc, protocol.ProtocolError))
    response_object = protocol.RemoteException.from_exception(exc)
    return fastapi.responses.JSONResponse(status_code=exc.http_status, content=response_object.dict())


@app.exception_handler(Exception)
def exception_handler_default(request: fastapi.Request, exc: Union[protocol.ProtocolError, protocol.RequestException]
                      ) -> fastapi.responses.JSONResponse:
    # Only print stack trace on protocol exception
    logger.error("Uncaught exception", exc_info=True)
    return exception_handler(request, protocol.InternalServerError(misc.str_exception(exc)))


def clear_cache():
    _cached_server_session.cache_clear()
    _cached_backup_session.cache_clear()
