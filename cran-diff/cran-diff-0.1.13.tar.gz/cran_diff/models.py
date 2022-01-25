from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


def db_connect(connect_string):
    return create_engine(connect_string)


def create_deals_table(engine):
    Base.metadata.create_all(engine)


class Packages(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    title = Column(Text, nullable=False)
    version = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=False)
    maintainer = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    bugreport = Column(String(255), nullable=False)
    package_type = Column(String(255), nullable=False)  # current or archived
    release_number = Column(Integer, nullable=False)
    last_modified = Column(DateTime, nullable=False)  # date db-entry modified


class Imports(Base):
    __tablename__ = "imports"
    id = Column(Integer, primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)


class Suggests(Base):
    __tablename__ = "suggests"
    id = Column(Integer, primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)


class Exports(Base):
    __tablename__ = "exports"
    id = Column(Integer, primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(String(255), nullable=False)


class Arguments(Base):
    __tablename__ = "arguments"
    id = Column(Integer, primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    function = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    default = Column(Text, nullable=False)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    category = Column(Text, nullable=False)
    text = Column(Text, nullable=False)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    topic = Column(Text, nullable=False)


class TagMembers(Base):
    __tablename__ = "tag_members"
    id = Column(Integer, primary_key=True, nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)


def setup_db(connect_string):
    engine = db_connect(connect_string)
    create_deals_table(engine)
