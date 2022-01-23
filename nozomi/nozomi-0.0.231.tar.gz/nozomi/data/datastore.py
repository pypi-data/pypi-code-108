"""
Nozomi
Datastore Module
Copyright Amatino Pty Ltd
"""
from nozomi.ancillary.immutable import Immutable
from nozomi.ancillary.database_credentials import DatabaseCredentials
from typing import Type, TypeVar, Any, Optional, Dict
from nozomi.data.sql_conforming import AnySQLConforming

T = TypeVar('T', bound='Datastore')


class Datastore:
    """An abstraction of a persistent data storage layer"""

    def __init__(
        self,
        credentials: DatabaseCredentials,
        debug: bool = False
    ) -> None:

        raise NotImplementedError

    connection = Immutable(lambda s: NotImplemented)
    cursor = Immutable(lambda s: NotImplemented)

    def refresh(self) -> None:
        """Connect or re-connect the underlying database connection"""
        raise NotImplementedError

    def execute(
        self,
        query: str,
        arguments: Optional[Dict[str, AnySQLConforming]] = None,
        atomic: bool = False,
        threadsafe: bool = False
    ) -> Optional[Any]:
        """
        Execute a supplied SQL query string with the supplied arguments. The
        Datastore will attempt to recover from broken connections in flight. If
        the query is denoted as atomic. That is, it is not transaction
        dependent.
        """
        raise NotImplementedError

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()
        return

    def commit(self) -> None:
        self.cursor.execute('commit')
        return

    def mogrify(self, query: str, arguments: Optional[Dict[str, Any]]) -> str:
        """Return a string compiled query"""
        return self.cursor.mogrify(query, arguments).decode()

    def rollback(self) -> None:
        """Roll back the current transaction"""
        self.cursor.execute('rollback')

    def start_transaction(self) -> None:
        """Start a database transaction"""
        self.cursor.execute('start transaction')

    @classmethod
    def from_config(cls: Type[T], configuration: Any):
        credentials = configuration.database_credentials
        return cls(credentials, configuration.debug)
