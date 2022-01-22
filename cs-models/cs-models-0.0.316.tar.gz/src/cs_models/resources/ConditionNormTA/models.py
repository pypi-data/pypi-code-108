from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    String,
)

from ...database import Base


class ConditionNormTAModel(Base):
    __tablename__ = "condition_norm_therapeutic_areas"

    id = Column(Integer, primary_key=True)
    condition_norm_cui = Column(String(128), nullable=False, index=True)
    therapeutic_area_id = Column(
        Integer,
        ForeignKey('therapeutic_areas.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("condition_norm_cui", "therapeutic_area_id"),)
