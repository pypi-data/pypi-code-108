import abc

from whizbang.domain.repository.sql_server.pyodbc_repository_base import IPyodbcRepository


class IPyodbcManager(metaclass=abc.ABCMeta):
    """The PyodbcManager interface"""


class PyodbcManager(IPyodbcManager):
    def __init__(self, repository: IPyodbcRepository):
        self._repository = repository

