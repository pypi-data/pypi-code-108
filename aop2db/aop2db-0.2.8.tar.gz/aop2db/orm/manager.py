"""Methods for managing the relational database."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from aop2db.orm.models import Base
from aop2db.utils import get_conn

logger = logging.getLogger(__name__)

CONN = get_conn()

if not database_exists(CONN):
    create_database(CONN)

engine = create_engine(CONN)
session = sessionmaker(bind=engine)


def rebuild_database() -> None:
    """Burn everything and builds the database."""
    drop_database()
    build_database()


def build_database() -> None:
    """Build the tables of the database."""
    logger.warning("Building database...")
    Base.metadata.create_all(bind=engine)


def drop_database() -> None:
    """Drop all of the associated tables in the database."""
    logger.warning("Dropping database...")
    Base.metadata.drop_all(bind=engine)
