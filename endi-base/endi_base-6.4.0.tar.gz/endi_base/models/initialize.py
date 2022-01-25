"""
    Initialization functions
"""
import warnings

from sqlalchemy.exc import SAWarning

from endi_base.models.base import DBSESSION
from endi_base.models.base import DBBASE



def initialize_sql(engine):
    """
        Initialize the database engine
    """
    DBSESSION.configure(bind=engine)
    DBBASE.metadata.bind = engine
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Setting the metadatas")
    DBBASE.metadata.create_all(engine)
    from transaction import commit
    commit()
    return DBSESSION


def configure_warnings():
    """
    Python warning system setup

    Turns the sqla warning about implicit cartesian product into an excetion,
    to be sure not to miss'em.

    If cartesian product is intentional, make it explicit.
    https://docs.sqlalchemy.org/en/14/changelog/migration_14.html#change-4737
    """
    warnings.filterwarnings(
        'error',
        category=SAWarning,
        # module='sqlalchemy.orm.relationships'
        module='sqlalchemy.sql.compiler',
        message='.*cartesian.*'
    )
