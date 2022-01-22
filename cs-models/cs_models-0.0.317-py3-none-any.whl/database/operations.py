# pylint: disable=duplicate-code
import os
import sshtunnel
import typing
from contextlib import contextmanager

from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.orm import Session

from ..aact_database import engine as engine_aact
from ..database import engine, get_engine_for_port

# Uncomment the logging statements to see the SQL
# queries that are made
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@contextmanager
def assert_sql(expected):
    stmts = []

    # pylint: disable=unused-argument
    def catch_queries(conn, cursor, statement, *args):
        stmts.append((statement, args[0]))

    event.listen(engine, "before_cursor_execute", catch_queries)

    yield

    if expected != stmts:
        raise AssertionError(f"Expected: {expected!r}, Got: {stmts!r}")


@contextmanager
def session_scope(db: typing.Optional[str] = None):
    """Provide a transactional scope around a
    series of operations."""
    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html
    if os.getenv("SSH_TUNNEL"):
        ssh_server = os.getenv("SSH_HOST")
        ssh_username = os.getenv("SSH_USERNAME")
        ssh_pkey_path = os.getenv("SSH_PKEY_PATH")
        remote_bind_address = os.getenv("MYSQL_HOST")
        with sshtunnel.SSHTunnelForwarder(
                (ssh_server, 22),
                ssh_username=ssh_username,
                ssh_pkey=ssh_pkey_path,
                remote_bind_address=(remote_bind_address, 3306),
        ) as tunnel:
            tunnel.start()
            bind_engine = get_engine_for_port(tunnel.local_bind_port)
            if db == "aact":
                bind_engine = engine_aact
            session = Session(bind=bind_engine)

            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
    else:
        bind_engine = engine
        if db == "aact":
            bind_engine = engine_aact
        session = Session(bind=bind_engine)

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def create(session, model, schema, obj):
    """Validates the `obj` against the `schema` and
    creates a new row."""
    data, errors = schema().load(obj)
    if errors:
        raise ValidationError(errors)

    instance = model(**data)
    session.add(instance)

    # https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
    # Committing every small operation is not ideal but
    # is needed since we have multiple workers and we don't
    # want stale "ids". Had we used `session.flush`,
    # then different workers may clash when it comes
    # to generating ids
    session.commit()

    # Not doing `schema.dump` because it leads to a `SELECT ..`
    # query to db.
    return instance


def get_or_create(session, model, schema, obj: typing.Dict) -> typing.Tuple:
    """Based on the `obj`, gets the corresponding row
    if it exists. If it doesn't exist, then creates
    a new row."""
    instance = session.query(model).filter_by(**obj).first()
    if instance:
        return instance, False

    data, errors = schema().load(obj)
    if errors:
        raise ValidationError(errors)

    instance = model(**data)
    session.add(instance)
    session.commit()
    return instance, True


def get_or_create_by_filter(
    session, model, schema, obj: typing.Dict, query_fields: typing.List[str]
) -> typing.Tuple:
    """Builds a "query filter" based on `obj` and `query_fields`. If a row
    exists for the "query filter", gets the corresponding row
    if it exists. If it doesn't exist, then creates
    a new row."""
    # Attempt to get the model instance based on the
    # `query_fields` in `obj`
    instance = (
        session.query(model)
        .filter_by(
            **{
                key: obj[key]
                for key in obj
                if key in query_fields or key == "id"
            }
        )
        .first()
    )
    if instance:
        return instance, False

    data, errors = schema().load(obj)
    if errors:
        raise ValidationError(errors)

    instance = model(**data)
    session.add(instance)
    session.commit()
    return instance, True


def update_or_create(
    session, model, schema, obj: typing.Dict, query_fields: typing.List[str]
) -> typing.Tuple:
    """Builds a "query filter" based on `obj` and `query_fields`. If a row
    exists for the "query filter" then updates the row with the `obj` values.
    If a row doesn't exist, then creates a new row with the
    values from `obj`."""
    # Attempt to get the model instance based on the
    # `query_fields` in `obj`
    instance = (
        session.query(model)
        .filter_by(
            **{
                key: obj[key]
                for key in obj
                if key in query_fields or key == "id"
            }
        )
        .first()
    )

    # Validate
    data, errors = schema().load(obj)
    if errors:
        raise ValidationError(errors)

    if instance:
        # Update
        for k, v in data.items():
            instance.__setattr__(k, v)
        session.commit()
        return instance, False

    # Create
    instance = model(**data)
    session.add(instance)
    session.commit()
    return instance, True


def bulk_save(session, instances: typing.List, batch_size: int = 5000):
    """
    Updates or Creates the model instances that are passed in.
    Note: The validation of the data should be done by the caller before
    preparing the model instances.

    https://stackoverflow.com/questions/19904176/transactions-and-sqlalchemy
    https://docs.sqlalchemy.org/en/13/_modules/examples/performance/bulk_inserts.html
    https://docs.sqlalchemy.org/en/13/faq/performance.html
    """
    # Need to do this to avoid `sqlalchemy.orm.exc.StaleDataError`
    # when some `instances` involve updates and not creates.
    # Ends up performing extra `SELECT` queries.
    session.flush()

    for i in range(0, len(instances), batch_size):
        batch = instances[i : i + batch_size]
        session.bulk_save_objects(batch)
    session.commit()
