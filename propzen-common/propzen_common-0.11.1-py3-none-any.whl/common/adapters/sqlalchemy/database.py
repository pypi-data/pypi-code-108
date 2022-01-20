from typing import Callable
from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import Session


class Database:
    """Database session manager"""

    def __init__(self, db_url: str) -> None:
        self._database_created = False
        self._engine = create_engine(db_url, pool_pre_ping=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self, metadata: MetaData, start_mappers: Callable) -> None:
        if not self._database_created:
            metadata.create_all(self._engine, checkfirst=True)
            start_mappers()
            self._database_created = True

    def session(self) -> Session:
        return self._session_factory()
