from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
)

from ...database import Base


class GNRSSModel(Base):
    __tablename__ = "gn_rss"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False)
    article_date = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
