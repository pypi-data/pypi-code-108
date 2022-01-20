from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    String,
    DECIMAL,
)

from ...database import Base


class DealOutboxModel(Base):
    __tablename__ = "deal_outbox"

    id = Column(Integer, primary_key=True)
    announcement_date = Column(DateTime, nullable=False)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=False,
    )
    round = Column(String(50), nullable=True)
    deal_value = Column(DECIMAL(13, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    company_sec_id = Column(
        Integer,
        ForeignKey('companies_sec.id'),
        nullable=False,
    )
    company_ous_id = Column(
        Integer,
        ForeignKey('companies_ous.id'),
        nullable=False,
    )
    investors = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
