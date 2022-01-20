from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Boolean,
)

from ...database import Base


class InterventionTypeModel(Base):
    __tablename__ = "intervention_type"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
        unique=True,
    )
    route = Column(String(50), nullable=True)
    modality = Column(String(256), nullable=True)
    dosage_form = Column(String(50), nullable=True)
    combination_therapy = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
