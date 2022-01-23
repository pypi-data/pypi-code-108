from __future__ import annotations
import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, DirectoryPath, PrivateAttr
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.sql.expression import Select
from .crypto import EncryptionProdiver

from typing import TYPE_CHECKING, Any, ClassVar, List, Dict, Tuple, Type

if TYPE_CHECKING:
    pass


class DataProvider(ABC):
    name: ClassVar[str]

    def __init__(self, params: Dict[str, Any] | None) -> None:
        super().__init__()

    @classmethod
    @property
    def supported_providers(cls) -> Dict[str, Type[DataProvider]]:
        def all_subclasses(cls) -> Dict[str, Type[DataProvider]]:
            subc = {} | {cl.name: cl for cl in cls.__subclasses__()}

            sub_subc = {}
            for c in subc.values():
                sub_subc |= all_subclasses(c)

            return subc | sub_subc

        return all_subclasses(cls)

    @abstractmethod
    def get_connection(
        self, user_id: int, encryption_provider: EncryptionProdiver = None
    ) -> DataConnection:
        pass

    @abstractmethod
    def check_data_exist(self, user_id: int) -> bool:
        pass

    @classmethod
    def get_data_provider(
        cls, name: str, params: Dict[str, Any] | None
    ) -> DataProvider:

        if name not in cls.supported_providers:
            raise NotImplementedError(f"Data provider {name} doesn't exist")

        return cls.supported_providers[name](params)


class DataConnection(ABC):
    def __init__(
        self,
        data_provider: DataProvider,
        user_id: int,
        encryption_provider: EncryptionProdiver | None,
    ) -> None:
        super().__init__()

        self._data_provider = data_provider
        self._user_id = user_id
        self._encryption_provider = encryption_provider

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def encrypted(self) -> bool:
        return self._encryption_provider is not None

    @abstractmethod
    def append_log(self, poll_code: str, log: str) -> bool:
        """Appends a single serialized `log` for a given `poll_code`"""
        pass

    def update_log(self, id: Any, log: str) -> bool:
        """Updates a log identified by `id` with a new serialized `log`"""
        raise NotImplementedError("This provider doesn't support row updates")

    def get_all_logs(self) -> List[Tuple[Any, str]]:
        """Get all serialized logs"""
        raise NotImplementedError("This provider doesn't support row updates")

    def get_log(self, id: Any) -> Tuple[Any, str]:
        """Get a single serialized log identified by `id`"""
        ret = self.get_logs([id])
        if len(ret) == 1:
            return ret[0]
        else:
            raise ValueError("Log id wasn't found")

    def get_logs(
        self,
        ids: List[Any],
    ) -> List[Tuple[Any, str]]:
        """Get a list of serialized logs identified by `ids`"""
        raise NotImplementedError("This provider doesn't support retrieving rows")

    def get_poll_logs(
        self,
        poll_code: str,
        date_from: datetime.datetime = None,
        date_to: datetime.datetime = None,
        max_rows: int = None,
    ) -> List[Tuple[Any, str]]:
        """Get a list of serialized logs for a given `poll_code` sorted by creation date, optionally filtered by `date_from`, `date_to` and optionally limited to `max_rows`"""
        raise NotImplementedError("This provider doesn't support retrieving rows")

    def get_last_n_logs(self, poll_code: str, count: int) -> List[Tuple[Any, str]]:
        return self.get_poll_logs(poll_code, max_rows=count)

    def get_last_logs(
        self, poll_code: str, date_from: datetime.datetime, max_rows: int
    ) -> List[Tuple[Any, str]]:
        return self.get_poll_logs(poll_code, date_from=date_from, max_rows=max_rows)


class SQLLiteProviderParams(BaseModel):
    base_path: DirectoryPath
    _base_uri: str = PrivateAttr(default="sqlite:///")

    class Config:
        extra = "forbid"


class SQLLiteProvider(DataProvider):
    name = "sqllite"

    def __init__(self, params: Dict[str, Any]) -> None:
        super().__init__(params)

        self._params = SQLLiteProviderParams.parse_obj(params)

    def get_connection(
        self, user_id: int, encryption_provider: EncryptionProdiver = None
    ) -> DataConnection:
        return SQLLiteConnection(self, user_id, encryption_provider)

    def check_data_exist(self, user_id: int) -> bool:
        base_path = self._params.base_path
        return base_path.joinpath("u" + str(user_id), "data.db").exists()


class SQLLiteConnection(DataConnection):
    def __init__(
        self,
        data_provider: SQLLiteProvider,
        user_id: int,
        encryption_provider: EncryptionProdiver = None,
    ) -> None:
        super().__init__(data_provider, user_id, encryption_provider)

        base_path = data_provider._params.base_path
        base_path.joinpath("u" + str(self.user_id)).mkdir(exist_ok=True)

        self._engine = engine = sa.create_engine(
            data_provider._params._base_uri
            + str(
                data_provider._params.base_path.joinpath(
                    "u" + str(self.user_id), "data.db"
                )
            )
        )

        self._meta = meta = sa.MetaData()

        self._data_table = data_table = sa.Table(
            "data",
            meta,
            sa.Column("id", sa.Integer, primary_key=True, index=True, nullable=False),
            sa.Column("poll_code", sa.String, index=True, unique=False, nullable=False),
            sa.Column("log", BLOB, nullable=False),
            sa.Column("created_ts", sa.DATETIME, nullable=False),
            sa.Column("updated_ts", sa.DATETIME, nullable=False),
        )

        with engine.connect() as conn:
            data_table.create(conn, checkfirst=True)

    def append_log(self, poll_code: str, log: str) -> bool:
        now = datetime.datetime.now()

        log_out = log.encode()
        if self.encrypted:
            log_out = self._encryption_provider.encrypt(log_out)

        stmt = self._data_table.insert(
            values={
                "log": log_out,
                "poll_code": poll_code,
                "created_ts": now,
                "updated_ts": now,
            }
        )

        with self._engine.connect() as conn:
            result = conn.execute(stmt)

            if result.rowcount == 1:
                return True
            else:
                return False

    def _query_and_decrypt(self, stmt: Select) -> List[Tuple[Any, str]]:
        ret = []
        with self._engine.connect() as conn:
            result = conn.execute(stmt)

            rows = result.all()
            for row in rows:
                if self.encrypted:
                    try:
                        ret.append(
                            (
                                row.id,
                                self._encryption_provider.decrypt(row.log).decode(),
                            )
                        )
                    except Exception:
                        continue
                else:
                    ret.append((row.id, row.log.decode()))

        return ret

    def get_logs(
        self,
        ids: List[Any],
    ) -> List[Tuple[Any, str]]:
        stmt = self._data_table.select().where(self._data_table.c.id.in_(ids))

        return self._query_and_decrypt(stmt)

    def update_log(self, id: Any, log: str) -> bool:
        now = datetime.datetime.now()

        log_out = log.encode()
        if self.encrypted:
            log_out = self._encryption_provider.encrypt(log_out)

        stmt = (
            self._data_table.update()
            .where(self._data_table.c.id == id)
            .values(log=log_out, updated_ts=now)
        )

        with self._engine.connect() as conn:
            result = conn.execute(stmt)

            if result.rowcount == 1:
                return True
            else:
                return False

    def get_all_logs(self) -> List[Tuple[Any, str]]:
        stmt = self._data_table.select()

        return self._query_and_decrypt(stmt)

    def get_poll_logs(
        self,
        poll_code: str,
        date_from: datetime.datetime = None,
        date_to: datetime.datetime = None,
        max_rows: int = None,
    ) -> List[Tuple[Any, str]]:
        stmt = self._data_table.select().where(
            self._data_table.c.poll_code == poll_code
        )

        if date_from:
            stmt = stmt.where(self._data_table.c.created_ts >= date_from)

        if date_to:
            stmt = stmt.where(self._data_table.c.created_ts <= date_to)

        if max_rows:
            stmt = stmt.limit(max_rows)

        return self._query_and_decrypt(stmt)
