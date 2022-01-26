# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base classes for requests in Invenio."""

import uuid

from invenio_db import db
from invenio_records.models import RecordMetadataBase
from sqlalchemy import func
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import String
from sqlalchemy_utils import UUIDType


class RequestMetadata(db.Model, RecordMetadataBase):
    """Base class for requests of any kind in Invenio."""

    __tablename__ = "request_metadata"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    number = db.Column(String(50), unique=True, index=True, nullable=True)

    expires_at = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
        default=None,
        nullable=True,
    )

    # TODO later
    # labels: maybe per-community CVs
    # assignees: enables notifications? no impact on permissions


class RequestEventModel(db.Model, RecordMetadataBase):
    """Request Events model."""

    __tablename__ = "request_events"

    type = db.Column(db.String(1), nullable=False)
    request_id = db.Column(
        UUIDType, db.ForeignKey(RequestMetadata.id, ondelete="CASCADE")
    )
    request = db.relationship(RequestMetadata)


class SequenceMixin:
    """Integer sequence generator.

    The purpose of this model is to generate a sequence of integers using the
    underlying database's auto increment features in a transaction friendly
    manner.

    The database table have a single column declared as auto-incrementing. To
    obtain a new value, we insert a row in the table and let the database
    assign a value to it.

    If two transactions try to insert the same value one will fail/retry.

    Usage:

    .. code-block:: python

        class MySequence(db.Model, SequenceMixin):
            __table_name__ = "mycounter"
    """

    @declared_attr
    def value(cls):
        """The counter."""
        return db.Column(
            db.BigInteger().with_variant(db.Integer, "sqlite"),
            primary_key=True, autoincrement=True
        )

    @classmethod
    def next(cls):
        """Return next available integer."""
        try:
            with db.session.begin_nested():
                obj = cls()
                db.session.add(obj)
        except IntegrityError:  # pragma: no cover
            with db.session.begin_nested():
                # Someone has likely modified the table without using the
                # models API. Let's fix the problem.
                cls._set_sequence(cls.max())
                obj = cls()
                db.session.add(obj)
        return obj.value

    @classmethod
    def max(cls):
        """Get max record identifier."""
        max_value = db.session.query(func.max(cls.value)).scalar()
        return max_value if max_value else 0

    @classmethod
    def _set_sequence(cls, val):
        """Internal function to reset sequence to specific value.

        Note: this function is for PostgreSQL compatibility.

        :param val: The value to be set.
        """
        if db.engine.dialect.name == 'postgresql':  # pragma: no cover
            db.session.execute(
                "SELECT setval(pg_get_serial_sequence("
                "'{0}', 'value'), :newval)".format(
                    cls.__tablename__), dict(newval=val))

    @classmethod
    def insert(cls, val):
        """Insert a record identifier.

        :param val: The value to insert.
        """
        with db.session.begin_nested():
            obj = cls(value=val)
            db.session.add(obj)
            cls._set_sequence(cls.max())


class RequestNumber(db.Model, SequenceMixin):
    """Request number sequence model."""

    __tablename__ = "request_number_seq"
