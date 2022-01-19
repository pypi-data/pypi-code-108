from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class HLTTermTAModel(Base):
    __tablename__ = "hlt_ta"

    id = Column(Integer, primary_key=True)
    hlt_id = Column(
        Integer,
        ForeignKey('hlt_terms.id'),
        nullable=False,
    )
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
