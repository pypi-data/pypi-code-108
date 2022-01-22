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


class InterventionConditionModel(Base):
    __tablename__ = "intervention_condition"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=False,
    )
    stage = Column(
        Integer,
        nullable=True,
    )
    geography = Column(
        String(50),
        nullable=True
    )
    line = Column(
        Integer,
        nullable=True
    )
    discontinued = Column(Boolean, nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
