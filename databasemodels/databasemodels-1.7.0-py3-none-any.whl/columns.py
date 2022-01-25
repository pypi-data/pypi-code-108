import re
from abc import ABC, abstractmethod
from dataclasses import Field
from typing import TYPE_CHECKING, Optional, Any

from psycopg import sql

if TYPE_CHECKING:
    from psycopg import connection


__all__ = [
    'Column',
    'ColumnType'
]


COLUMN_NAME = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]{0,58}')


class Column:
    def __init__(self, name: str, type: 'ColumnType') -> None:
        self.name = name
        self.type = type

    def initialize(self, conn: 'connection.Connection[Any]') -> None:
        self.type.initializeType(conn)

    @property
    def columnDefinition(self) -> 'sql.Composable':
        return sql.SQL('{} {}').format(sql.Identifier(self.name), self.type.typeStatement)

    @classmethod
    def fromField(cls, field: 'Field[Any]') -> 'Column':
        assert COLUMN_NAME.match(field.name) is not None, f'{field.name} is not a valid column name'
        assert field.name != 'conn', 'Column name must not be "conn"'

        assert isinstance(field.type, ColumnType), 'Fields must be annotated with a type deriving ColumnType'

        return cls(field.name, field.type)

    @property
    def rawType(self) -> str:
        return self.type.rawType

    def __str__(self) -> str:
        return f'"{self.name}" {self.type}'


class ColumnType(ABC):
    """
    Defines the types of data that is allowed in a column of a model.
    """

    @property
    @abstractmethod
    def typeStatement(self) -> 'sql.Composable':
        ...

    @property
    def primary(self) -> bool:
        return False

    @property
    @abstractmethod
    def rawType(self) -> str:
        ...

    @abstractmethod
    def initializeType(self, conn: 'connection.Connection[Any]') -> None:
        ...

    @abstractmethod
    def convertDataFromString(self, conn: 'connection.Connection[Any]', string: Optional[str]) -> Any:
        """
        Convert string retrieved from the database to a Python object representation.
        Should be the inverse of convertInsertableFromData.

        :param conn: the connection to use
        :type conn: psycopg.connection.Connection
        :param string: the string to convert
        :type string: Optional[str]
        :return: the Python object
        :rtype: Any
        """

    def convertInsertableFromData(self, conn: 'connection.Connection[Any]', data: Any) -> Any:
        """
        Convert a Python object representation to something insertable by psycopg.
        Should be the inverse of convertDataFromString.

        :param conn: the connection to use
        :type conn: psycopg.connection.Connection
        :param data: the object to convert
        :type data: Any
        :return: the insertable object
        :rtype: Any
        """
        return data