from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class ClinicalDataOutboxModel(Base):
    __tablename__ = "clinical_data_outbox"

    id = Column(Integer, primary_key=True)
    date = Column(
        DateTime,
        nullable=False
    )
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
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=True,
    )
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=True,
    )
    stage = Column(
        Integer,
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
