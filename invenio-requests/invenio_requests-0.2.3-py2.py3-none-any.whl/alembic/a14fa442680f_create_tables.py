#
# Copyright (C) 2021 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = "a14fa442680f"
down_revision = "5cd30a3503c9"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "request_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(
                    none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "id", UUIDType(), nullable=False
        ),
        sa.Column("number", sa.String(length=50), nullable=True),
        sa.Column(
            "expires_at",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_request_metadata")),
    )
    op.create_index(
        op.f("ix_request_metadata_number"),
        "request_metadata",
        ["number"],
        unique=True,
    )
    op.create_table(
        "request_events",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "id", UUIDType(), nullable=False
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(
                    none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=1), nullable=False),
        sa.Column(
            "request_id", UUIDType(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["request_metadata.id"],
            name=op.f("fk_request_events_request_id_request_metadata"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_request_events")),
    )
    op.create_table(
        "request_number_seq",
        sa.Column(
            "value",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("value", name=op.f("pk_request_number_seq")),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("request_number_seq")
    op.drop_table("request_events")
    op.drop_index(
        op.f("ix_request_metadata_number"), table_name="request_metadata"
    )
    op.drop_table("request_metadata")
