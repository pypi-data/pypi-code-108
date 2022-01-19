from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from ...database import Base


class InterventionDescModel(Base):
    __tablename__ = "intervention_desc"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    desc = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
