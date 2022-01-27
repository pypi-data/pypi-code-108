from typing import List

from django.db import models
from psycopg2 import sql


def truncate_sql(model: models.Model):
    """
    SQL to truncate this table
    BE CAREFUL!
    """
    statement = sql.SQL("TRUNCATE {table} CASCADE;").format(table=sql.Identifier(model._meta.db_table))
    return statement


def upsert_sql(model: models.Model, exclude_fields: List[str] = None):
    """
    Generates an UPSERT (update-on-conflict) statement
    to import from the "osm" schema which is the default
    import target of pgosm-flex
    """

    table = sql.Identifier(model._meta.db_table)
    field_names = [f.db_column or f.get_attname() for f in model._meta.fields]

    for ex in exclude_fields or []:
        if ex in field_names:
            field_names.remove(ex)

    fields = sql.SQL(",").join([sql.Identifier(f) for f in field_names])

    source_table = sql.Identifier(
        model._meta.db_table.replace("osmflex_", "")
        .replace("point", "_point")
        .replace("line", "_line")
        .replace("polygon", "_polygon")
        .replace("publictransport", "public_transport")
        .replace("roadmajor", "road_major")
    )

    # This is the update clause...
    update_clause = sql.SQL("DO UPDATE SET\n\t") + sql.SQL(",").join(
        [sql.Identifier(f) + sql.SQL(" = Excluded.") + sql.Identifier(f) for f in field_names]
    )

    statement = sql.SQL(
        """
    INSERT INTO {table}
        ({fields})
    SELECT {fields} FROM {source_schema}.{source_table}
    ON CONFLICT
        ON CONSTRAINT {constraint}
        {update_clause}
        WHERE {table}.osm_id = Excluded.osm_id
    """
    ).format(
        table=table,
        fields=fields,
        source_table=source_table,
        update_clause=update_clause,
        source_schema=sql.Identifier("osm"),
        constraint=sql.Identifier(f"{model._meta.db_table}_pkey"),
    )

    return statement
