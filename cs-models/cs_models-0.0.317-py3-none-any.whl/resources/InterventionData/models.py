from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
    Boolean,
)

from ...database import Base


class InterventionDataModel(Base):
    __tablename__ = "intervention_data"

    id = Column(Integer, primary_key=True)
    source_type = Column(
        String(50),
        nullable=False
    )
    date = Column(DateTime, nullable=True)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    pubmed_id = Column(
        Integer,
        ForeignKey('pubmed.id'),
        nullable=True,
    )
    file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=True,
    )
    title = Column(String(255), nullable=True)
    orig_file_url = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
