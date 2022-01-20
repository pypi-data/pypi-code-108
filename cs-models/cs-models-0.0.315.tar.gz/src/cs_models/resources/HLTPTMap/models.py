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


class HLTPTMapModel(Base):
    __tablename__ = "hlt_pt_map"

    id = Column(Integer, primary_key=True)
    hlt_id = Column(
        Integer,
        ForeignKey('hlt_terms.id'),
        nullable=False,
    )
    pt_code = Column(String(128), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("hlt_id", "pt_code"),)
