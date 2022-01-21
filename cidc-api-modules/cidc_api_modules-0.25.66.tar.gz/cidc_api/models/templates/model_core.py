__all__ = [
    "cimac_id_to_cimac_participant_id",
    "get_property",
    "identity",
    "MetadataModel",
    "with_default_session",
]

from functools import wraps
from typing import Any, Dict, Optional, Tuple

from flask import current_app
from sqlalchemy.orm import Session

from ...config.db import BaseModel

# some simple functions to handle common process_as cases
# the parameters for all process_as functions are
# value : Any, context : dict[Column, Any]
identity = lambda v, _: v
cimac_id_to_cimac_participant_id = lambda cimac_id, _: cimac_id[:7]

# this is a special-case handler, where any property in context
# can be retrieved by using get_property(< key >) as a process_as function
# # created to get the `object_url` of files after GCS URI formatting
get_property = lambda prop: lambda _, context: (
    [v for k, v in context.items() if k.name == prop] + [None]
)[0]


def with_default_session(f):
    """
    For some `f` expecting a database session instance as a keyword argument,
    set the default value of the session keyword argument to the current app's
    database driver's session. We need to do this in a decorator rather than
    inline in the function definition because the current app is only available
    once the app is running and an application context has been pushed.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        if "session" not in kwargs:
            kwargs["session"] = current_app.extensions["sqlalchemy"].db.session
        return f(*args, **kwargs)

    return wrapped


class MetadataModel(BaseModel):
    __abstract__ = True

    def primary_key_values(self) -> Optional[Tuple[Any]]:
        """
        Returns a tuple of the values of the primary key values
        Special value None if all of the pk columns are None
        """
        pk_map = self.primary_key_map()
        return tuple(pk_map.values()) if pk_map is not None else None

    def primary_key_map(self) -> Optional[Dict[str, Any]]:
        """
        Returns a dict of Column: value for any primary key column.
        Special value None if all of the pk columns are None
        """
        from .utils import _all_bases

        columns_to_check = [c for c in self.__table__.columns]
        for c in _all_bases(type(self)):
            if hasattr(c, "__table__"):
                columns_to_check.extend(c.__table__.columns)

        primary_key_values = {}
        for column in columns_to_check:
            if column.primary_key:
                value = getattr(self, column.name)
                primary_key_values[column] = value

        if all(v is None for v in primary_key_values.values()):
            return None  # special value

        return primary_key_values

    def unique_field_values(self) -> Optional[Tuple[Any]]:
        """
        Returns a tuple of all values that are uniquely constrained (pk or unique).
        Special value None if all of the unique columns are None
        """
        from .utils import _all_bases

        columns_to_check = [c for c in self.__table__.columns]
        for c in _all_bases(type(self)):
            if hasattr(c, "__table__"):
                columns_to_check.extend(c.__table__.columns)

        unique_field_values = []
        for column in columns_to_check:
            # column.primary_key == True for 1+ column guaranteed
            if column.unique or column.primary_key:
                value = getattr(self, column.name)
                unique_field_values.append(value)

        if all(v is None for v in unique_field_values):
            return None  # special value

        return tuple(unique_field_values)

    def merge(self, other):
        """
        Merge column values from other into self, raising an error on conflicts between non-null fields.
        Special handling for JSONB columns where dicts are combined, erroring if overlapping values conflict.
        """
        if self.__class__ != other.__class__:
            raise Exception(
                f"cannot merge {self.__class__} instance with {other.__class__} instance"
            )

        # also need to handle columns for all superclasses
        from .utils import _all_bases

        for column in self.__table__.columns + [
            c
            for b in _all_bases(type(self))
            if hasattr(b, "__table__")
            for c in b.__table__.columns
        ]:
            if hasattr(self, column.name):
                current = getattr(self, column.name)
                incoming = getattr(other, column.name)

                # sqlalchemy unwraps JSONB to dict behind the scenes
                if isinstance(current, dict) and isinstance(incoming, dict):
                    # make a deepcopy to make sure it's a faithful copy
                    from copy import deepcopy

                    old = deepcopy(current)

                    # update and reset the value
                    current.update(incoming)
                    setattr(self, column.name, current)

                    # update incoming with the original, faithful copy from this instance
                    # that way, current and incoming will disagree if any values overlap
                    # do this after we update current to make sure that it's unaffected
                    incoming.update(old)

                if current is None:
                    setattr(self, column.name, incoming)
                elif incoming is not None and current != incoming:
                    pks = {
                        col.name: value for col, value in self.primary_key_map().items()
                    }
                    raise Exception(
                        f"found conflicting values for {self.__class__.__name__} {pks} for {column.name} : {current}!={incoming}"
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict of all non-null columns (by name) and their values"""
        # avoid circular imports
        from .utils import _all_bases

        columns_to_check = [c for c in type(self).__table__.columns]
        for b in _all_bases(type(self)):
            if hasattr(b, "__table__"):
                columns_to_check.extend(b.__table__.columns)

        ret = {
            c.name: getattr(self, c.name)
            for c in columns_to_check
            if hasattr(self, c.name)
        }
        ret = {k: v for k, v in ret.items() if v is not None}
        return ret

    @classmethod
    @with_default_session
    def get_by_id(cls, *id, session: Session):
        """
        Returns an instance of this class with given the primary keys if it exists
        Special value None if no instance in the table matches the given values
        """
        with current_app.app_context():
            ret = session.query(cls).get(id)
        return ret
