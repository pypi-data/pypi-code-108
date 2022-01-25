"""
This module contains the :mod:`sqlalchemy` :class:`sqlalchemy.engine.Engine` and :class:`sqlalchemy.orm.Session`.
"""

import typing as t
from os import environ

import lazy_object_proxy
import sqlalchemy.engine
import sqlalchemy.orm

# noinspection PyTypeChecker
engine: sqlalchemy.engine.Engine = lazy_object_proxy.Proxy(lambda: sqlalchemy.create_engine(environ["IS_DB_URI"]))
# noinspection PyTypeChecker
Session: t.Type[sqlalchemy.orm.Session] = lazy_object_proxy.Proxy(lambda: sqlalchemy.orm.sessionmaker(bind=engine))
