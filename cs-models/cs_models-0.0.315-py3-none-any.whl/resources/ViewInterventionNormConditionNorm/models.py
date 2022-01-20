from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    UniqueConstraint,
)

from ...database import Base


class ViewInterventionNormConditionModel(Base):
    __tablename__ = "_view_intervention_norm_condition_norm"

    id = Column(Integer, primary_key=True)
    intervention_norm_cui = Column(String(191), nullable=False, index=True)
    condition_norm_cui = Column(String(128), nullable=False, index=True)
    condition_norm_cui_name = Column(String(191), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("intervention_norm_cui", "condition_norm_cui"),)
