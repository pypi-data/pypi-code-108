from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)

from ...database import Base


class ConditionEpidemiologyModel(Base):
    __tablename__ = "condition_epidemiology"

    id = Column(Integer, primary_key=True)
    source_date = Column(DateTime, nullable=False)
    source_title = Column(Text, nullable=False)
    source_name = Column(String(128), nullable=False)
    source_table = Column(String(50), nullable=False)
    source_table_id = Column(Integer, nullable=False)
    pubmed_id = Column(
        Integer,
        ForeignKey('pubmed.id'),
        nullable=True,
    )
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    measure = Column(String(50), nullable=False)
    geographic_area = Column(String(50))
    snippet = Column(Text, nullable=False)
    statistic = Column(Float)
    statistic_text = Column(String(128))
    year = Column(String(50))
    population_type = Column(String(128))
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
