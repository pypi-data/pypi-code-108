from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
)

from ...database import Base


class ConditionNormModel(Base):
    __tablename__ = "condition_norm"

    id = Column(Integer, primary_key=True)
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=False,
    )
    condition_norm_cui = Column(String(128), nullable=False, index=True)
    condition_norm_cui_name = Column(String(191), nullable=False, index=True)
    condition_norm_cui_broader = Column(String(128), nullable=False, index=True)
    condition_norm_cui_name_broader = Column(String(191), nullable=False, index=True)
    condition_norm_name = Column(String(191), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
