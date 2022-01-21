from typing import Optional

from sqlalchemy import create_engine, Table
from sqlalchemy.schema import CreateSchema
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from creds import postgres_url, mysql_url
from sessionize.utils.sa_orm import get_table


def setup(connection_string: str, schema: Optional[str] = None) -> tuple[Engine, Table]:
    Base = declarative_base()

    engine = create_engine(connection_string, echo=False)

    if schema is not None:
        if schema not in engine.dialect.get_schema_names(engine.connect()):
               engine.execute(CreateSchema(schema))

    class People(Base):
        __tablename__ = 'people'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(20))
        age = Column(Integer)
        if schema is not None:
            __table_args__ = {'schema': schema}

    class Places(Base):
        __tablename__ = 'places'
        id = Column(Integer, primary_key=True, autoincrement=True)
        address = Column(String(100))
        if schema is not None:
            __table_args__ = {'schema': schema}

    Base.metadata.reflect(bind=engine, schema=schema)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine, tables=[People.__table__, Places.__table__])

    people = [
        People(name='Olivia', age=17),
        People(name='Liam', age=18),
        People(name='Emma', age=19),
        People(name='Noah', age=20),
    ]

    with Session(engine) as session, session.begin():
        session.add_all(people)
   
    return engine, get_table('people', engine, schema=schema)


def sqlite_setup(path='sqlite:///data/test.db', schema=None) -> tuple[Engine, Table]:
    return setup(path, schema=schema)


def postgres_setup(postgres_url=postgres_url, schema=None) -> tuple[Engine, Table]:
    path = postgres_url
    return setup(path, schema=schema)


def mysql_setup(shema=None) -> tuple[Engine, Table]:
    path = mysql_url
    return setup(path, schema=shema)