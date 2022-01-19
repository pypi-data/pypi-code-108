from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class PubmedInterventionModel(Base):
    __tablename__ = "pubmed_interventions"

    id = Column(Integer, primary_key=True)
    pubmed_id = Column(
        Integer,
        ForeignKey('pubmed.id'),
        nullable=False,
    )
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
