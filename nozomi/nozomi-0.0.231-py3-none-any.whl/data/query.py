"""
Nozomi
Query Module
Copyright Amatino Pty Ltd
"""
from typing import Type, TypeVar, Dict, Optional, Union
from collections.abc import Sequence, Mapping
from nozomi.data.datastore import Datastore
from nozomi.data.sql_conforming import AnySQLConforming

T = TypeVar('T', bound='Query')


class Query:
    """An SQL query"""

    def __init__(
        self,
        query: str,
    ) -> None:

        assert isinstance(query, str)
        self._query = query

        return

    def execute(
        self,
        datastore: Datastore,
        arguments: Optional[Dict[str, AnySQLConforming]] = None,
        dynamic_arguments: Optional[Dict[str, str]] = None,
        atomic: bool = False,
        threadsafe: bool = False,
        mogrify: bool = False
    ) -> Optional[Union[Sequence, Mapping]]:
        query = self._query
        if dynamic_arguments is not None:
            query = self._query.format(**dynamic_arguments)
        if mogrify is True:
            print(datastore.mogrify(
                query=query,
                arguments=arguments
            ))
        return datastore.execute(
            query=query,
            arguments=arguments,
            atomic=atomic,
            threadsafe=threadsafe
        )

    def mogrify(
        self,
        datastore: Datastore,
        arguments: Optional[Dict[str, AnySQLConforming]] = None,
        dynamic_arguments: Optional[Dict[str, str]] = None
    ) -> str:
        query = self._query
        if dynamic_arguments is not None:
            query = self._query.format(**dynamic_arguments)
        return datastore.mogrify(query, arguments)

    @classmethod
    def from_file(
        cls: Type[T],
        filename: str
    ) -> T:

        with open(filename) as qfile:
            query = qfile.read()

        return cls(query=query)

    @classmethod
    def optionally_from_file(
        cls: Type[T],
        filename: str
    ) -> Optional[T]:

        try:
            with open(filename) as qfile:
                query = qfile.read()
        except FileNotFoundError:
            return None

        return cls(query=query)

    @classmethod
    def require(
        cls: Type[T],
        query: Optional[T],
        name: str = 'required'
    ) -> T:
        if not isinstance(query, Query):
            raise NotImplementedError('Missing {n} query'.format(n=name))

        return query
