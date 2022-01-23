from time import time
from typing import List, Optional, cast

from flypper.entities.flag import Flag, FlagData, UnversionedFlagData
from flypper.storage.abstract import AbstractStorage
from sqlalchemy import Table
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select
from sqlalchemy.sql.schema import MetaData
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    JSON,
)

_VERSION_KEY = "version"

class MissingTable(Exception):
    pass

class SqlAlchemyStorage(AbstractStorage):
    _flags_table: Optional[Table] = None
    _metadata_table: Optional[Table] = None

    def __init__(
        self,
        engine: Optional[Engine] = None,
        session: Optional[Session] = None,
    ):
        if self.__class__._flags_table is None:
            raise MissingTable("Use SqlAlchemyStorage.build_flags_table first")
        if self.__class__._metadata_table is None:
            raise MissingTable("Use SqlAlchemyStorage.build_metadata_table first")
        if not engine and not session:
            raise ValueError("Either engine or session must be provided")

        self._engine = engine
        self._session = session
        self._flags: Table = self.__class__._flags_table
        self._metadata: Table = self.__class__._metadata_table

    def list(self, version__gt: int = 0) -> List[Flag]:
        statement = (
            select([self._flags.c.name, self._flags.c.data])
            .select_from(self._flags)
            .where(self._flags.c.version > version__gt)
        )
        return [
            Flag(data=self._parse_row_into_flag_data(row))
            for row in self._connection.execute(statement).fetchall()
        ]

    def upsert(self, flag_data: UnversionedFlagData) -> Flag:
        conn = self._connection
        with conn.begin():
            # Insert the new version row to get a new id == version
            version = self._increment_version(conn)
            # Select the flag for update, to look if it exists
            flag_name = flag_data["name"]
            existing_row = conn.execute(
                select([self._flags.c.name, self._flags.c.data])
                .select_from(self._flags)
                .where(self._flags.c.name == flag_name)
                .with_for_update()
            ).fetchone()
            flag = Flag(data={
                "name": flag_data["name"],
                "deleted": flag_data["deleted"],
                "enabled": flag_data["enabled"],
                "enabled_for_actors": flag_data["enabled_for_actors"],
                "enabled_for_percentage_of_actors": flag_data["enabled_for_percentage_of_actors"],
                "updated_at": time(),
                "version": version,
            })
            if existing_row:
                # Update the flag
                conn.execute(
                    self._flags.update()
                    .where(self._flags.c.name == flag_name)
                    .values(data=flag.data, version=version)
                )
            else:
                # Insert the flag
                conn.execute(
                    self._flags.insert(),
                    name=flag.name,
                    version=version,
                    data=flag.data,
                )
            return flag

    def delete(self, flag_name: str) -> None:
        self._connection.execute(
            self._flags.delete()
            .where(self._flags.c.name == flag_name)
        )

    def _increment_version(self, conn):
        existing_row = conn.execute(
            select([self._metadata.c.key, self._metadata.c.value])
            .select_from(self._metadata)
            .where(self._metadata.c.key == _VERSION_KEY)
            .with_for_update()
        ).fetchone()
        if existing_row:
            # Increment the existing version
            next_version = int(existing_row["value"]) + 1
            conn.execute(
                self._metadata.update()
                .where(self._metadata.c.key == _VERSION_KEY)
                .values(value=str(next_version))
            )
        else:
            # Insert the first version
            next_version = 1
            conn.execute(
                self._metadata.insert(),
                key=_VERSION_KEY,
                value=str(next_version),
            )
        return next_version

    def _parse_row_into_flag_data(self, row) -> FlagData:
        data = row["data"]
        enabled_for_actors = {
            "actor_key": data["enabled_for_actors"]["actor_key"],
            "actor_ids": data["enabled_for_actors"]["actor_ids"],
        } if data["enabled_for_actors"] else None
        enabled_for_percentage_of_actors = {
            "actor_key": data["enabled_for_percentage_of_actors"]["actor_key"],
            "percentage": data["enabled_for_percentage_of_actors"]["percentage"],
        } if data["enabled_for_percentage_of_actors"] else None
        return cast(FlagData, {
            "name": row["name"],
            "deleted": data["deleted"],
            "enabled": data["enabled"],
            "enabled_for_actors": enabled_for_actors,
            "enabled_for_percentage_of_actors": enabled_for_percentage_of_actors,
            "updated_at": data["updated_at"],
            "version": data["version"],
        })

    @property
    def _connection(self) -> Connection:
        if self._session:
            return self._session.connection()
        elif self._engine:
            return self._engine.connect()
        else:
            raise ValueError("No engine nor session found")

    @classmethod
    def build_metadata_table(cls, sqla_metadata: MetaData) -> Table:
        cls._metadata_table = Table(
            "flypper_metadata",
            sqla_metadata,
            Column("key", String, primary_key=True),
            Column("value", String, nullable=False),
        )
        return cls._metadata_table

    @classmethod
    def build_flags_table(cls, sqla_metadata: MetaData) -> Table:
        cls._flags_table = Table(
            "flypper_flags",
            sqla_metadata,
            Column("name", String, primary_key=True),
            Column("version", Integer, nullable=False),
            Column("data", JSON, nullable=False),
        )
        return cls._flags_table
