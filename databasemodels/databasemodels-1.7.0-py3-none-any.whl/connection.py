import pickle

from typing import Union, TYPE_CHECKING, Optional, Callable, Any, cast, overload
from typing_extensions import TypedDict
from pathlib import Path, PurePath
from psycopg import connect

from functools import wraps

if TYPE_CHECKING:
    from psycopg import connection


__all__ = [
    'Login',
    'connectWithLogin',
    'createLogin',
    'loadLogin',
    'createOrLoadLogin',
    'createConnection',
    'loadConnection',
    'createOrLoadConnection'
]


class Login(TypedDict):
    dbname: str
    user: str
    password: str
    host: str
    port: int


PathLike = Union[str, PurePath]


def processPath(pathlike: PathLike) -> 'Path':
    return Path(pathlike)


def prompt(prompt: str, default: Optional[str] = None) -> str:
    if default is not None:
        value = input(f'{prompt} [{default}]: ')

        if value:
            return value
        return default
    else:
        return input(f'{prompt}: ')


def connectWithLogin(login: Login) -> 'connection.Connection[Any]':
    return connect(**login)


def connectUsingLoginFunc(func: Callable[[PathLike], Login]) -> Callable[[PathLike], 'connection.Connection[Any]']:
    @wraps(func)
    def wrapper(filePath: PathLike) -> 'connection.Connection[Any]':
        return connectWithLogin(func(filePath))

    return wrapper


def createLogin(filePath: PathLike) -> Login:
    path = processPath(filePath)

    login = dict(
        dbname=prompt('Database Name'),
        user=prompt('User Name'),
        password=prompt('Password'),
        host=prompt('Hostname'),
        port=int(prompt('Port', '5432'))
    )

    with path.open('wb') as loginFile:
        pickle.dump(login, loginFile)

    return cast(Login, login)


def loadLogin(filePath: PathLike) -> Login:
    path = processPath(filePath)

    with path.open('rb') as loginFile:
        return cast(Login, pickle.load(loginFile))


def createOrLoadLogin(filePath: PathLike) -> Login:
    path = processPath(filePath)

    if path.exists():
        return loadLogin(filePath)
    else:
        return createLogin(filePath)


createConnection = connectUsingLoginFunc(createLogin)
loadConnection = connectUsingLoginFunc(loadLogin)
createOrLoadConnection = connectUsingLoginFunc(createOrLoadLogin)
