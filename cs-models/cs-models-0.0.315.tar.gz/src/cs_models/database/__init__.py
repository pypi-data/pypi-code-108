import os
import boto3
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


def _get_ssm_parameters():
    result = {}
    session = boto3.Session(region_name="us-east-1")
    ssm = session.client("ssm")
    ssm_parameters = ssm.get_parameters(
        Names=["mysqlHost", "mysqlUser", "mysqlPassword", "mysqlDB"],
        WithDecryption=True | False,
    )["Parameters"]
    for parameter in ssm_parameters:
        result[parameter["Name"]] = parameter["Value"]
    return result


def _get_credentials():
    result = {
        "mysqlHost": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "mysqlUser": os.getenv("MYSQL_USER", "root"),
        "mysqlPassword": os.getenv("MYSQL_PASSWORD", "testpass"),
        "mysqlDB": os.getenv("MYSQL_DB", "dev_db"),
    }
    if os.getenv("FLASK_CONFIGURATION") == "production":
        result = _get_ssm_parameters()
    return result


def _get_mysql_uri(port: Optional[int] = None):
    environment = os.getenv("FLASK_CONFIGURATION")
    if environment in ("testing", "ci"):
        return "sqlite://"

    credentials = _get_credentials()
    if port:
        return "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4" % (
            credentials["mysqlUser"],
            credentials["mysqlPassword"],
            "127.0.0.1",
            str(port),
            credentials["mysqlDB"],
        )
    return "mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4" % (
        credentials["mysqlUser"],
        credentials["mysqlPassword"],
        credentials["mysqlHost"],
        credentials["mysqlDB"],
    )


def get_engine_for_port(port):
    return create_engine(_get_mysql_uri(port), convert_unicode=True)


def import_models():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # this usually happens when a model declares a FK constraint but the
    # referenced table hasn't been created yet
    # import src.cs_models.resources.all_models  # noqa
    pass


mysql_db_uri = _get_mysql_uri()
engine = create_engine(mysql_db_uri, convert_unicode=True)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()
