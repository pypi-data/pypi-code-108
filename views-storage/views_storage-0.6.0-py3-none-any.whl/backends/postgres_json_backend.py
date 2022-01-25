
from typing import Union, Dict, List
import sqlalchemy as sa
from sqlalchemy.engine import Engine
from . import storage_backend

KeyType = Union[str, int]
JsonSerializable = Union[
        Dict["JsonSerializable","JsonSerializable"],
        List["JsonSerializable"],
        str, int, float, bool, None]

class PostgresJsonBackend(storage_backend.StorageBackend[KeyType, JsonSerializable]):

    def __init__(self, engine: Engine, table_name: str, schema: str = "public"):
        self._engine = engine
        self._metadata = sa.MetaData(schema = schema)
        self._table = sa.Table(table_name, self._metadata, autoload_with = self._engine)
        self._assert_one_pk()

    @property
    def _primary_key(self):
        return self._table.primary_key.columns[0]

    @property
    def fields(self):
        return [(c.name, c.type) for c in self._table.columns]

    def store(self, key: KeyType, value: JsonSerializable) -> None:
        with self._engine.connect() as con:
            values = {self._primary_key.name: key, **value}
            query = self._table.insert().values(**values)
            con.execute(query)

    def retrieve(self, key: KeyType) -> JsonSerializable:
        with self._engine.connect() as con:
            query = self._table.select().where(self._primary_key == key)
            res = con.execute(query).fetchone()
            return dict(res) if res is not None else None

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
