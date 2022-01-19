from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
)

from ...database import Base


class HLTTermModel(Base):
    __tablename__ = "hlt_terms"

    id = Column(Integer, primary_key=True)
    hlt_code = Column(String(128), nullable=False, index=True)
    hlt_name = Column(String(191), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
