from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    String,
)

from ...database import Base


class DesignationModel(Base):
    __tablename__ = "designations"

    id = Column(Integer, primary_key=True)
    intervention_condition_id = Column(
        Integer,
        ForeignKey('intervention_condition.id'),
        nullable=False,
    )
    designation = Column(String(128), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
