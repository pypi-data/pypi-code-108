from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Boolean,
)

from ...database import Base


class InterventionNormModel(Base):
    __tablename__ = "intervention_norm"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    norm_cui = Column(String(191), nullable=False, index=True)
    norm_cui_name = Column(String(191), nullable=False)
    is_deleted = Column(Boolean, nullable=True)
    is_combination_element = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("intervention_id"),)

