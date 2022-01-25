from typing import TYPE_CHECKING, Any, Union, Tuple, Optional, Dict, OrderedDict, \
    Generator, Type, List, ContextManager

from psycopg import sql
from typing_extensions import Protocol, runtime_checkable

from .helper import classproperty

if TYPE_CHECKING:
    from psycopg import connection
    from .columns import Column

__all__ = [
    'Dataclass',
    'DatabaseModel'
]


@runtime_checkable
class Dataclass(Protocol):
    __dataclass_fields__: Dict[str, Any]


# Properties gave warnings in PyCharm, this disables checking that inspection
# noinspection PyPropertyDefinition
@runtime_checkable
class DatabaseModel(Dataclass, Protocol):
    __column_definitions__: OrderedDict[str, 'Column']
    __primary_key__: Optional['Column']

    __schema_name__: str
    __table_name__: str

    __instance_cache__: Dict[Any, 'DatabaseModel']

    @classmethod
    def createTable(cls, conn: 'connection.Connection[Any]', *, recreateSchema: bool = False, recreateTable: bool = False) -> None:
        """
        Create a table representing this class.

        :param conn: the connection to use
        :type conn: psycopg.connection.Connection
        :param recreateSchema: if true it will drop the schema before recreating it. This will drop any other tables on the schema too
        :type recreateSchema: bool
        :param recreateTable: if true it will drop the table before recreating it. This will drop any other tables that depend on it
        :type recreateTable: bool
        """

    @classmethod
    def instantiateAll(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> Tuple['DatabaseModel', ...]:
        """
        Instantiate all models of this type with the given query.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param query: the additional query to use after the select statement
        :type query: Union[str, sql.Composable]
        :return: a tuple of every model returned from the query
        :rtype: Tuple[DatabaseModel, ...]
        """

    @classmethod
    def instantiateOne(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> 'DatabaseModel':
        """
        Instantiate one model of this type with the given query.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param query: the additional query to use after the select statement
        :type query: Union[str, sql.Composable]
        :return: a model
        :rtype: DatabaseModel
        """

    @classmethod
    def instantiate(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> Generator['DatabaseModel', None, None]:
        """
        Instantiate each models of this type with the given query as a generator.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param query: the additional query to use after the select statement
        :type query: Union[str, sql.Composable]
        :return: a tuple of every model returned from the query
        :rtype: Tuple[DatabaseModel, ...]
        """

    @classmethod
    def instantiateFromPrimaryKey(cls, conn: 'connection.Connection[Any]', primaryKey: Any) -> 'DatabaseModel':
        """
        Instantiate a model from a given primary key. The model must have a primary key and the given primaryKeyColumn
        must correspond to a value.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param primaryKey: the primary key to look up
        :type primaryKey: Any
        :return: the model
        :rtype: DatabaseModel
        """

    def insert(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
        """
        Insert this model into the database.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param doTypeConversion: if true a conversion function will be called on each field
        :type doTypeConversion: bool
        """

    def update(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
        """
        Update this model in the database, will replace any model currently in the database with the updated values.
        If there was not a row with the primary key this model has it will raise an error.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param doTypeConversion: if true a conversion function will be called on each field
        :type doTypeConversion: bool
        """

    def insertOrUpdate(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
        """
        Intelligently either updates or inserts this model into the database. If there was not a row with the primary
        key this model has it will insert it.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :param doTypeConversion: if true a conversion function will be called on each field
        :type doTypeConversion: bool
        """

    def delete(self, conn: 'connection.Connection[Any]') -> bool:
        """
        Delete this model from the database and return whether or not it was deleted.

        :param conn: the connection to use
        :type conn: connection.Connection[Any]
        :return: if the model was deleted
        :rtype: bool
        """

    @classmethod
    def getColumn(cls, name: str) -> 'Column':
        """
        Get a Column from a given name from this model type.

        :param name: the name of the column
        :type name: str
        :return: the column with the given name
        :rtype: Column
        """

    @classproperty
    def primaryKeyColumn(cls: Type['DatabaseModel']) -> Optional['Column']:
        """
        Get the primary key for this model or model type.

        :return: either the primary key column or None
        :rtype: Optional[Column]
        """

    @property
    def primaryKey(self) -> Optional[Any]:
        """
        Get this model's primary key value or None if there is no primary key.

        :return: the primary key value
        :rtype: Optional[Any]
        """

    @classproperty
    def schema(cls: Type['DatabaseModel']) -> str:
        """
        Get the schema for this model.

        :return: the schema this model uses
        :rtype: str
        """

    @classproperty
    def table(cls: Type['DatabaseModel']) -> str:
        """
        Get the table name for this model.

        :return: the table name this model uses
        :rtype: str
        """

    @classproperty
    def columns(cls: Type['DatabaseModel']) -> List['Column']:
        """
        Get all columns for this model.

        :return: a list of columns
        :rtype: List[Column]
        """

    def mutate(self, conn: 'connection.Connection[Any]', updateOnExit: bool) -> ContextManager[None]:
        """
        Enter a context manager which inserts or updates the model at the end of it if no errors occurred

        :param conn: the connection to use
        :type conn: connection.Connection
        :param updateOnExit: wether or not to update upon a successful update
        :type updateOnExit: bool
        """
