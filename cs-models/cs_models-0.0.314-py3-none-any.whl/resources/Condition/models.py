from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    ForeignKey,
)

from ...database import Base


class ConditionModel(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True)
    disease_id = Column(String(128), nullable=False)
    disease_name = Column(String(191), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("disease_id"),)
