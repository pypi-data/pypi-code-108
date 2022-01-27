from os import environ

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base


from .secrets import get_secrets_manager

db = SQLAlchemy()
BaseModel = declarative_base(bind=db)
db.Model = BaseModel


def init_db(app: Flask):
    """Connect `app` to the database and run migrations"""
    db.init_app(app)
    db.Model = BaseModel
    Migrate(app, db, app.config["MIGRATIONS_PATH"])
    with app.app_context():
        upgrade(app.config["MIGRATIONS_PATH"])


def get_sqlalchemy_database_uri(testing: bool = False) -> str:
    """Get the PostgreSQL DB URI from environment variables"""

    db_uri = environ.get("POSTGRES_URI")
    if testing:
        # Connect to the test database
        db_uri = environ.get("TEST_POSTGRES_URI", "fake-conn-string")
    elif not db_uri:
        secrets = get_secrets_manager(testing)

        # If POSTGRES_URI env variable is not set,
        # we're connecting to a Cloud SQL instance.

        config: dict = {
            "drivername": "postgresql",
            "username": environ.get("CLOUD_SQL_DB_USER"),
            "password": secrets.get("CLOUD_SQL_DB_PASS"),
            "database": environ.get("CLOUD_SQL_DB_NAME"),
        }

        if environ.get("CLOUD_SQL_INSTANCE_NAME"):
            socket_dir = environ.get("CLOUD_SQL_SOCKET_DIR", "/cloudsql/")

            # If CLOUD_SQL_INSTANCE_NAME is defined, we're connecting
            # via a unix socket from inside App Engine.
            config["query"] = {
                "host": f'{socket_dir}{environ.get("CLOUD_SQL_INSTANCE_NAME")}'
            }
        else:
            raise Exception(
                "Either POSTGRES_URI or CLOUD_SQL_INSTANCE_NAME must be defined to connect "
                + "to a database."
            )

        db_uri = str(URL(**config))

    assert db_uri

    return db_uri
