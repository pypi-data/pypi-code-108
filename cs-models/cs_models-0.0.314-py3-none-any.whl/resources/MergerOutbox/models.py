from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    DECIMAL
)

from ...database import Base


class MergerOutboxModel(Base):
    __tablename__ = "merger_outbox"

    id = Column(Integer, primary_key=True)
    announcement_date = Column(DateTime, nullable=False)
    news_id = Column(Integer, ForeignKey('newswires.id'), nullable=False)
    target_sec_id = Column(Integer, ForeignKey('companies_sec.id'),
                           nullable=True)
    target_ous_id = Column(Integer, ForeignKey('companies_ous.id'),
                           nullable=True)
    acquirer_sec_id = Column(Integer, ForeignKey('companies_sec.id'),
                             nullable=True)
    acquirer_ous_id = Column(Integer, ForeignKey('companies_ous.id'),
                             nullable=True)
    deal_value = Column(DECIMAL(13, 2), nullable=True)
    type = Column(String(50), nullable=True)
    offer_price = Column(Float, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
