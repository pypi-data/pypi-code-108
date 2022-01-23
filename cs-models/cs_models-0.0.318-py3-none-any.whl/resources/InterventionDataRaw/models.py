from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
    Boolean,
)

from ...database import Base


class InterventionDataRawModel(Base):
    __tablename__ = "intervention_data_raw"

    id = Column(Integer, primary_key=True)
    source_type = Column(
        String(50),
        nullable=False
    )
    source_id = Column(Integer, nullable=False)
    insight_type = Column(
        String(50), nullable=False,
    )
    insight_name = Column(
        String(191),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
