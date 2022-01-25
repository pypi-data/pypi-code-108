from typing import Optional

from sqlalchemy import create_engine, Table, ForeignKey
from sqlalchemy.schema import CreateSchema
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from creds import postgres_url, mysql_url
from sessionize.utils.sa_orm import get_table, get_schemas


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
        address_id = Column(Integer)
        if schema is not None:
            __table_args__ = {'schema': schema}

    class Places(Base):
        __tablename__ = 'places'
        id = Column(Integer, primary_key=True, autoincrement=True)
        address = Column(String(100))
        city = Column(String(30))
        state = Column(String(2))
        zipcode = Column(Integer)

        if schema is not None:
            __table_args__ = {'schema': schema}

    Base.metadata.reflect(bind=engine)
    Base.metadata.drop_all(bind=engine)
    for sch in get_schemas(engine):
        Base.metadata.reflect(bind=engine, schema=sch)
        Base.metadata.drop_all(bind=engine)
    Base.metadata.reflect(bind=engine, schema=sch)
    Base.metadata.create_all(bind=engine, tables=[People.__table__, Places.__table__])

    people = [
        People(name='Olivia', age=17, address_id=1),
        People(name='Liam', age=18, address_id=1),
        People(name='Emma', age=19, address_id=2),
        People(name='Noah', age=20, address_id=2),
    ]

    places = [
        Places(address='1600 Pennsylvania Avenue NW', city='San Antonio', state='TX', zipcode=78205),
        Places(address='300 Alamo Plaza', city='Washington', state='DC', zipcode=20500),
    ]

    with Session(engine) as session, session.begin():
        session.add_all(people)
        session.add_all(places)
   
    return engine, get_table('people', engine, schema=schema)


def sqlite_setup(path='sqlite:///data/test.db', schema=None) -> tuple[Engine, Table]:
    return setup(path, schema=schema)


def postgres_setup(postgres_url=postgres_url, schema=None) -> tuple[Engine, Table]:
    path = postgres_url
    return setup(path, schema=schema)


def mysql_setup(shema=None) -> tuple[Engine, Table]:
    path = mysql_url
    return setup(path, schema=shema)