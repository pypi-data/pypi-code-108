from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
)

from ...database import Base


class BiomarkerSynModel(Base):
    __tablename__ = "biomarker_syns"

    id = Column(Integer, primary_key=True)
    biomarker_id = Column(
        Integer,
        ForeignKey('biomarkers.id'),
        nullable=False,
    )
    synonym = Column(
        String(191),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
