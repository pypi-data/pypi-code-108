from sqlalchemy import (
    Column,
    Integer,
    DateTime,
)
from datetime import datetime

from ...database import Base


class NewswireCompanyUpdateOutboxModel(Base):
    __tablename__ = 'newswire_company_update_outbox'

    id = Column(Integer, primary_key=True)
    news_id = Column(
        Integer,
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
