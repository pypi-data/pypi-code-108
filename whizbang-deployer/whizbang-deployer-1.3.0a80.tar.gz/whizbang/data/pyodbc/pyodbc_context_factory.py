import abc

from whizbang.core.context_factory_base import ContextFactoryBase, IContextFactory
from whizbang.data.pyodbc.pyodbc_context_args import SqlServerContextArgs
from whizbang.data.pyodbc.pyodbc_context import PyodbcContext


class IPyodbcContextFactory(IContextFactory, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_context(self, context_args, context_type: str) -> PyodbcContext:
        """get_context interface"""


class PyodbcContextFactory(ContextFactoryBase, IPyodbcContextFactory):

    def get_context(self, context_args: SqlServerContextArgs, type: str = None) -> PyodbcContext:
        context = PyodbcContext(
            server=context_args.server,
            database=context_args.database,
            username=context_args.username,
            password=context_args.password)
        return context
