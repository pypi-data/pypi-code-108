from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Boolean,
)

from ...database import Base


class InterventionPharmActionModel(Base):
    __tablename__ = "intervention_pharm_action"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    pharm_action_id = Column(
        Integer,
        ForeignKey('pharm_actions.id'),
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

    __table_args__ = (UniqueConstraint("intervention_id", "pharm_action_id"),)
