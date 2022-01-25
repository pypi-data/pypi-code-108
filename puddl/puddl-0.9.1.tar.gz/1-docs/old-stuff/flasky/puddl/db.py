import logging

from sqlalchemy import create_engine, Column, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from puddl import Datum

log = logging.getLogger(__name__)

Base = declarative_base()


class Stream(Base):
    __tablename__ = "stream"
    id = Column(Integer, primary_key=True)
    source = Column(Text, index=True, nullable=False)  # e.g. "f@obs"
    meta = Column(JSONB, nullable=False)
    created_dt = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return f"{self.source}: {self.best_guess_timestamp}"

    @property
    def best_guess_timestamp(self):
        # TODO infer from meta
        return self.created_dt


class DB:
    def __init__(self):
        from puddl import config

        db_args = config.get("db")
        self.url = URL(**db_args)
        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def drop_all_tables(self):
        Base.metadata.drop_all(self.engine)

    def is_ok(self):
        try:
            self.engine.execute("SELECT 1")
            log.info("Connection OK")
            return True
        except OperationalError as e:
            log.error(str(e))
            return False

    def migrate(self):
        # Alembic!
        # for now: create stuff
        Base.metadata.create_all(self.engine)

    def stream_simple(self, source, meta):
        stream = Stream(
            source=source,
            meta=meta,
        )
        self.session.add(stream)
        self.session.commit()

    def stream_datum(self, source, d: Datum):
        stream = Stream(
            source=source,
            meta=d.data,
        )
        self.session.add(stream)
        self.session.commit()
