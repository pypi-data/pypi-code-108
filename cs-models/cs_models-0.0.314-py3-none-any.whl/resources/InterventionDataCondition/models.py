from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from ...database import Base


class InterventionDataConditionModel(Base):
    __tablename__ = "intervention_data_condition"

    id = Column(Integer, primary_key=True)
    intervention_data_id = Column(
        Integer,
        ForeignKey('intervention_data.id'),
        nullable=False,
    )
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint('intervention_data_id', 'condition_id'),)
