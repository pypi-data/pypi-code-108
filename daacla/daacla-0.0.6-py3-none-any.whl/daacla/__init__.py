
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, Optional, Tuple, Type, TypeVar, Union
import os
import re
import sqlite3
import sys

from appdirs import user_data_dir

TableInstance = Any
TableClass = Type[TableInstance]

T = TypeVar('T')


@dataclass
class Meta:
    table: str
    fields: Dict[str, Type]
    key: Optional[str] = None

    def __hash__(self) -> int:
        return id(self)

    def __post_init__(self) -> None:
        self.columns = {}
        for name, tipe in self.fields.items():
            col = f'{_type_to_type(tipe)}'
            if name == self.key:
                col += ' PRIMARY KEY'
            self.columns[name] = col

    @property
    def ddl(self) -> str:
        cs = map(lambda it: ' '.join(it), self.columns.items())
        csj = ', '.join(cs)
        return f"""CREATE TABLE IF NOT EXISTS {self.table} ({csj})"""

    def validate_key(self) -> str:
        if self.key is None:
            raise Exception(f'Primary key is not defined: {self.table}')
        return self.key

    def values(self, instance: TableInstance) -> Tuple[Any, ...]:
        return tuple(map(lambda it: getattr(instance, it), self.fields.keys()))

    def set_values(self, instance: TableInstance, values: Dict[str, Any]) -> None:
        for k, v in values.items():
            setattr(instance, k, v)


def table(key: Optional[str] = None) -> Callable[[Type], TableClass]:
    '''Decorator

    import daacla

    @dataclass
    @daacla.table(key='a')
    class HogeMoge:
        a: str
        b: int
        c: Optional[bool] = None
    '''

    def decorate(klass: Type) -> TableClass:
        table = _snake_case(klass.__name__)
        klass.__daacla = Meta(
            key=key,
            table=table,
            fields=klass.__annotations__
        )
        return klass
    return decorate


def _snake_case(s: str) -> str:
    return '_'.join(map(str.lower, re.findall(r'''[A-Z][a-z0-9]*''', s)))


def _is_instance_of_daacla(instance: Any) -> bool:
    return hasattr(instance, '__daacla')


def _type_to_type(t: Type) -> str:
    # Datatypes In SQLite Version 3 - https://www.sqlite.org/datatype3.html
    if t == str:
        return 'TEXT'
    if t == float:
        return 'REAL'
    if t == bool:
        return 'BOOL'
    return 'INTEGER'


def _n_place_holders(n: int) -> str:
    return ', '.join(['?'] * n)


@dataclass
class Daacla:
    path: Optional[str] = None

    @staticmethod
    def on_user_data_dir(app_name: str, author: str) -> 'Daacla':
        path = os.path.join(user_data_dir(app_name, author), 'daacla.sqlite')
        return Daacla(path=path)

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = os.path.join(sys.path[0], 'daacla.sqlite')
        if not self.path == ':memory:':
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.connection = sqlite3.connect(self.path, isolation_level=None)
        self._ready: Dict[Meta, bool] = defaultdict(bool)

    def delete(self, klass: Type[T], key: Any) -> bool:
        meta = self.prepare_table(klass)
        key_column = meta.validate_key()
        q = f"""DELETE FROM {meta.table} WHERE {key_column} = ?"""
        cur = self.connection.execute(q, (key, ))
        return cur.rowcount == 1

    def exists(self, klass: Type[T], key: Any) -> bool:
        return self.get(klass, key) is not None

    def get(self, klass: Type[T], key: Any) -> Optional[T]:
        meta = self.prepare_table(klass)
        key_column = meta.validate_key()
        q = f"""SELECT {', '.join(meta.fields.keys())} FROM {meta.table} WHERE {key_column} = ?"""
        cur = self.connection.cursor()
        for t in cur.execute(q, (key,)):
            params = {}
            for k, v in zip(meta.fields.keys(), t):
                params[k] = v
            return klass(**params)  # type: ignore
        return None

    def truncate(self, klass: TableClass) -> None:
        meta = self.prepare_table(klass)
        self.connection.execute(f'DELETE FROM {meta.table}')

    @staticmethod
    def in_memory(**kwargs: Any) -> 'Daacla':
        return Daacla(path=':memory:', **kwargs)  # type: ignore

    def insert(self, instance: TableInstance) -> None:
        meta = self.prepare_table(instance)
        place_holders = ', '.join(['?'] * len(meta.fields.keys()))
        self.connection.execute(
            f'''INSERT INTO {meta.table} ({', '.join(meta.fields.keys())}) VALUES ({place_holders})''',
            meta.values(instance)
        )

    def meta(self, instance_or_klass: Union[TableInstance, TableClass]) -> Meta:
        if not _is_instance_of_daacla(instance_or_klass):
            raise Exception('Not a Daacla instance. Use `@daacla.table` decorator')
        return getattr(instance_or_klass, '__daacla')

    def prepare_table(self, klass: TableClass) -> Meta:
        meta = self.meta(klass)

        if not self._ready[meta]:
            self.connection.execute(meta.ddl)
            self._ready[meta] = True

        return meta

    def update(self, instance: TableInstance, **kwargs: Any) -> bool:
        meta = self.prepare_table(instance)
        key_column = meta.validate_key()
        meta.set_values(instance, kwargs)

        key_value = getattr(instance, key_column)
        pairs = map(lambda kv: '='.join(kv), zip(meta.fields.keys(), ['?'] * len(meta.fields)))
        q = f'''UPDATE {meta.table} SET {', '.join(pairs)} WHERE {key_column} = ?'''
        cur = self.connection.execute(q, (*meta.values(instance), key_value))
        return cur.rowcount == 1

    def upsert(self, instance: TableInstance, **kwargs: Any) -> bool:
        meta = self.prepare_table(instance)
        _ = meta.validate_key()
        meta.set_values(instance, kwargs)

        q = f'''REPLACE INTO {meta.table} ({', '.join(meta.fields.keys())}) VALUES ({_n_place_holders(len(meta.fields))})'''
        cur = self.connection.execute(q, meta.values(instance))
        return cur.rowcount == 1

    def select(self, klass: Type[T], expression: str, *args: Any) -> Iterator[T]:
        meta = self.prepare_table(klass)
        q = f"""SELECT {', '.join(meta.fields.keys())} FROM {meta.table} WHERE {expression}"""
        cur = self.connection.cursor()
        for t in cur.execute(q, args):
            params = {}
            for k, v in zip(meta.fields.keys(), t):
                params[k] = v
            yield klass(**params)  # type: ignore
