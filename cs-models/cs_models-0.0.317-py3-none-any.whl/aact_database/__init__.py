import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

postgres_db_uri = "postgres+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
    user=os.getenv("AACT_USER", "root"),
    password=os.getenv("AACT_PASSWORD", "testpass"),
    host=os.getenv("AACT_HOST", "127.0.0.1"),
    port=5432,
    db=os.getenv("AACT_DB", "aact"),
)
engine = create_engine(postgres_db_uri, convert_unicode=True)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()
