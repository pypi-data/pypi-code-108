from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
)

from ...database import Base


class BiomarkerModel(Base):
    __tablename__ = "biomarkers"

    id = Column(Integer, primary_key=True)
    cui = Column(
        String(50),
        nullable=False,
    )
    type = Column(
        String(20),
        nullable=False
    )
    approved_name = Column(
        String(256),
        nullable=False
    )
    approved_symbol = Column(
        String(50),
        nullable=True
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
