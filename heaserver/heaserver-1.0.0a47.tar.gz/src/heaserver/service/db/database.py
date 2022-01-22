import abc
import configparser
from aiohttp import web
from typing import Optional


class Database(abc.ABC):

    @abc.abstractmethod
    def __init__(self, app: web.Application, config: Optional[configparser.ConfigParser]) -> None:
        pass
