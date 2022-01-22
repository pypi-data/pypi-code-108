from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
)

from ...database import Base


class ViewConditionByTAModel(Base):
    __tablename__ = "_view_condition_by_ta"

    id = Column(Integer, primary_key=True)
    ta_id = Column(Integer, nullable=False, index=True)
    hlt_name = Column(String(128), nullable=False, index=True)
    disease_name = Column(String(191), nullable=False)
    disease_id = Column(String(128), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
