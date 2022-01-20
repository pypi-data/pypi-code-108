from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
)

from ...database import Base


class InterventionConditionBiomarkerModel(Base):
    __tablename__ = "intervention_condition_biomarkers"

    id = Column(Integer, primary_key=True)
    intervention_condition_id = Column(
        Integer,
        ForeignKey('intervention_condition.id'),
        nullable=False,
    )
    biomarker_id = Column(
        Integer,
        ForeignKey('biomarkers.id'),
        nullable=False,
    )
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
