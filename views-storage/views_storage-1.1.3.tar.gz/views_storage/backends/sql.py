
from typing import Optional, Union, Dict
import sqlalchemy as sa
from sqlalchemy.engine import Engine, Connection
from views_storage import types
from . import storage_backend

KeyType = Union[str, int]

class Sql(storage_backend.StorageBackend[KeyType, Dict[str, types.JsonSerializable]]):

    def __init__(self, engine: Engine, table_name: str, schema: Optional[str] = None):
        self._engine = engine
        md_args = {"schema": schema} if schema is not None else {}
        self._metadata = sa.MetaData(**md_args)
        try:
            self._table = sa.Table(table_name, self._metadata, autoload_with = self._engine)
        except sa.exc.NoSuchTableError:
            raise KeyError(f"Table {table_name} does not exist")
        self._assert_one_pk()

    @property
    def _primary_key(self):
        return self._table.primary_key.columns[0]

    @property
    def fields(self):
        return [(c.name, c.type) for c in self._table.columns]

    def store(self, key: KeyType, value: Dict[str, types.JsonSerializable]) -> None:
        self._validate(value)
        with self._engine.connect() as con:
            if self._retrieve(con, key) is not None:
                self._delete(con, key)
            return self._store(con, key, value)

    def retrieve(self, key: KeyType) -> Dict[str, types.JsonSerializable]:
        with self._engine.connect() as con:
            try:
                assert (data := self._retrieve(con, key)) is not None
            except AssertionError:
                raise KeyError(f"Data for {key} does not exist")
            return data

    def exists(self, key: KeyType) -> bool:
        with self._engine.connect() as con:
            return self._exists(con, key)

    def keys(self):
        with self._engine.connect() as con:
            return con.execute(sa.select(self._primary_key)).fetchall()

    def _retrieve(self, con: Connection, key: KeyType):
        query = self._table.select().where(self._primary_key == key)
        res = con.execute(query).fetchone()
        if res is not None:
            data = dict(res)
            del data[self._primary_key.name]
            return data
        else:
            return None

    def _store(self, con: Connection, key: KeyType, value: Dict[str, types.JsonSerializable]):
        values = {self._primary_key.name: key, **value}
        query = self._table.insert().values(**values)
        con.execute(query)

    def _exists(self, con: Connection, key: KeyType) -> bool:
        return self._retrieve(con, key) is not None

    def _delete(self, con: Connection, key: KeyType):
        query = self._table.delete().where(self._primary_key == key)
        con.execute(query)

    def _validate(self, data: Dict[str, types.JsonSerializable]):
        for key in data.keys():
            try:
                names = [f for f,_ in self.fields]
                assert key in names
            except AssertionError:
                raise ValueError((
                    f"Field {key} not present in target table "
                    f"(Available fields: {', '.join(names)})"
                    ))
            try:
                data_sa_types = self._py_sa_type(type(data[key]))

                right_type = False
                for accepted_type in data_sa_types :
                    right_type |= isinstance(self._table.columns[key].type, accepted_type)
                assert right_type
            except AssertionError:
                raise ValueError((
                    f"Provided data field {key} is of wrong type "
                    f"(Got {data_sa_types}, expected {self._table.columns[key].type})"
                    ))

    def _assert_one_pk(self):
        try:
            _,*excess = [c.name for c in self._table.primary_key.columns]
            assert len(excess) == 0
        except AssertionError:
            raise ValueError("The database table has a composite primary key, which is not currently supported")

    def _py_sa_type(self, python_type):
        equivalent = {
                int: (sa.INTEGER, sa.FLOAT, sa.INT),
                str: (sa.TEXT, sa.VARCHAR, sa.CHAR),
                dict: (sa.JSON,),
                list: (sa.ARRAY,),
                bool: (sa.BOOLEAN,),
            }

        return equivalent[python_type]
