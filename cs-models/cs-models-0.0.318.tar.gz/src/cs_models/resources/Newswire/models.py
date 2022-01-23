from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class NewswireModel(Base):
    __tablename__ = 'newswires'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    tzinfo = Column(String(10))
    source = Column(String(128))
    headline = Column(Text)
    drugs = Column(Text)
    conditions = Column(Text)
    concepts = Column(Text)
    filtered_drugs = Column(Text)
    filtered_conditions = Column(Text)
    news_file_id = Column(Integer, ForeignKey("files.id"))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
