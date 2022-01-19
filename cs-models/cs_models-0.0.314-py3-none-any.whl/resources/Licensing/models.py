from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    String,
    Text,
)

from ...database import Base


class LicensingModel(Base):
    __tablename__ = "licensing"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    originator_subsidiary_id = Column(
        Integer,
        ForeignKey('subsidiaries.id'),
        nullable=False,
    )
    target_subsidiary_id = Column(
        Integer,
        ForeignKey('subsidiaries.id'),
        nullable=False,
    )
    type = Column(String(128), nullable=False)
    terms = Column(Text, nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
