from contextlib import contextmanager
from ..graph_database import driver


@contextmanager
def session_scope():
    """Provide a transactional scope around a
    series of operations."""

    session = driver.session()
    try:
        yield session
    except Exception:
        raise
    finally:
        session.close()
