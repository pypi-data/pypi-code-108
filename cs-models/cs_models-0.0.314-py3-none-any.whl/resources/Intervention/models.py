from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    Boolean,
)

from ...database import Base


class InterventionModel(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True)
    intervention_uid = Column(String(191), nullable=False)
    marketing_category = Column(String(50), nullable=True)
    preferred_term = Column(String(191), nullable=False)
    intervention_type = Column(String(128), nullable=True)
    intervention_url = Column(String(255), nullable=True)
    discontinued = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("intervention_uid"),)
