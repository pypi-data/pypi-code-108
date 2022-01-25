import logging

import sqlalchemy.orm

from impressive_strawberry.database import engine

log = logging.getLogger(__name__)

__all__ = (
    "dep_dbsession",
)


def dep_dbsession() -> sqlalchemy.orm.Session:
    """
    Dependency which creates a new database session (transaction) and closes it after the request is answered.
    """
    log.debug("Creating database session...")
    with engine.Session(future=True) as session:
        log.debug("Yielding control of the database session...")
        yield session
        log.debug("Closing database session...")
    log.debug("Closed database session!")
