
from typing import Optional, Union
import sqlalchemy as sa
from sqlalchemy.engine import Engine
from views_storage import types
from . import storage_backend

KeyType = Union[str, int]

class Sql(storage_backend.StorageBackend[KeyType, types.JsonSerializable]):

    def __init__(self, engine: Engine, table_name: str, schema: Optional[str] = None):
        self._engine = engine
        md_args = {"schema": schema} if schema is not None else {}
        self._metadata = sa.MetaData(**md_args)
        self._table = sa.Table(table_name, self._metadata, autoload_with = self._engine)
        self._assert_one_pk()

    @property
    def _primary_key(self):
        return self._table.primary_key.columns[0]

    @property
    def fields(self):
        return [(c.name, c.type) for c in self._table.columns]

    def store(self, key: KeyType, value: types.JsonSerializable) -> None:
        with self._engine.connect() as con:
            values = {self._primary_key.name: key, **value}
            query = self._table.insert().values(**values)
            con.execute(query)

    def retrieve(self, key: KeyType) -> types.JsonSerializable:
        with self._engine.connect() as con:
            query = self._table.select().where(self._primary_key == key)
            res = con.execute(query).fetchone()
            if res is not None:
                data = dict(res)
                del data[self._primary_key.name]
                return data
            else:
                return None

    def exists(self, key: KeyType) -> bool:
        return self.retrieve(key) is not None

    def keys(self):
        with self._engine.connect() as con:
            return con.execute(sa.select(self._primary_key)).fetchall()

    def _assert_one_pk(self):
        try:
            _,*excess = [c.name for c in self._table.primary_key.columns]
            assert len(excess) == 0
        except AssertionError:
            raise ValueError("The database table has a composite primary key, which is not currently supported")
