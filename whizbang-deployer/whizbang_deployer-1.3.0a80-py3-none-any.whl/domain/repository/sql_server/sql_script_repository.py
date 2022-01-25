import abc

import sqlparse

from whizbang.data.pyodbc.pyodbc_context import PyodbcContext
from whizbang.data.pyodbc.pyodbc_context_args import SqlServerContextArgs
from whizbang.data.pyodbc.pyodbc_context_factory import IPyodbcContextFactory
from whizbang.domain.repository.sql_server.pyodbc_repository_base import IPyodbcRepository, PyodbcRepositoryBase
from whizbang.util.sql_helpers import parse_sql


class ISqlScriptRepository(IPyodbcRepository, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute_script(self, context_args: SqlServerContextArgs, script: str):
        """execute sql statements against a sql database"""


class SqlScriptRepository(PyodbcRepositoryBase, IPyodbcRepository):
    def __init__(self, context_factory: IPyodbcContextFactory):
        PyodbcRepositoryBase.__init__(self, context_factory)

    def execute_script(self, context_args: SqlServerContextArgs, script: str):
        statements = sqlparse.split(script)
        result = self.__execute_statements(context_args, statements)
        return result

    def __execute_statements(self, context_args: SqlServerContextArgs, statements: 'list[str]'):
        context: PyodbcContext = self._get_context(context_args)
        result = context.execute_statements(statements)
        return result
