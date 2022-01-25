"""
This module contains some useful shortcuts for common database interactions.
"""

# TODO: improve this

import typing as t

import pydantic
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

import impressive_strawberry.web.errors as errors

DatabaseObject = t.TypeVar("DatabaseObject")
PydanticObject = t.TypeVar("PydanticObject")


def quick_create(session: Session, obj: DatabaseObject) -> DatabaseObject:
    """
    Add an object to the session, then commit it, and finally refresh the object before returning it.

    :param session: The session to use.
    :param obj: The object to quick save.
    :return: The committed and refreshed object.
    """

    session.add(obj)
    session.commit()
    session.refresh(obj)  # Useful for triggers and similar things!
    return obj


def quick_retrieve(session: Session, table: t.Type[DatabaseObject], **filters) -> DatabaseObject:
    """
    Query the database for the object satisfying the specified filters.

    :param session: The session to use.
    :param table: The table to query.
    :param filters: The filters to use in the query.
    :raise fastapi.HTTPException: Returns a ``404 Not Found`` status if no object is found, and a ``500 Internal Server Error`` status if multiple objects are found.
    :return: The retrieved object.
    """
    result = session.execute(
        select(table).filter_by(**filters)
    ).scalar()
    if not result:
        raise errors.ResourceNotFound()
    return result


def quick_update(session: Session, obj: DatabaseObject, data: pydantic.BaseModel) -> DatabaseObject:
    """
    Apply to the database object the changes from the passed :mod:`pydantic` model, then commit and refresh the object.

    :param session: The session to use.
    :param obj: The object to update.
    :param data: The data to update the object with.
    :return: The committed and refreshed object.
    """

    for key, value in data.dict().items():
        setattr(obj, key, value)

    session.commit()
    session.refresh(obj)
    return obj
