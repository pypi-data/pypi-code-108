import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def get_session(config):
    quoted = urllib.parse.quote_plus('DRIVER={driver};Server={host};Database={db};UID={user};PWD={password};TDS_Version=7.3;Port=1433;'.format(
        driver=config.driver, host=config.host, db=config.db, user=config.user, password=config.password))
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    engine.connect()

    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)

    return session


def get_base():
    return Base
