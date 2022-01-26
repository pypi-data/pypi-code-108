
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
import json

Base = declarative_base()

class Entry(Base):
    __tablename__ = 'model'
    __table_args__ = {
        "mysql_charset": "utf8"
    }
    id = Column(String, primary_key=True, index=True, unique=True)
    content = Column(String)
    def __repr__(self):
        return json.dumps({
            "id": self.id,
            "content": self.content
        })

class Flow(Base):
    __tablename__ = 'flow'
    __table_args__ = {
        "mysql_charset": "utf8"
    }
    id = Column(String, primary_key=True, index=True, unique=True)
    content = Column(String)
    def __repr__(self):
        return json.dumps({
            "id": self.id,
            "content": self.content
        })