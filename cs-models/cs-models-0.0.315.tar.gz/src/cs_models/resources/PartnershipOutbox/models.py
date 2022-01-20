from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    DECIMAL
)

from ...database import Base


class PartnershipOutboxModel(Base):
    __tablename__ = "partnership_outbox"

    id = Column(Integer, primary_key=True)
    announcement_date = Column(DateTime, nullable=False)
    news_id = Column(Integer, ForeignKey('newswires.id'), nullable=False)
    partner_one_sec_id = Column(Integer, ForeignKey('companies_sec.id'),
                           nullable=True)
    partner_one_ous_id = Column(Integer, ForeignKey('companies_ous.id'),
                           nullable=True)
    partner_two_sec_id = Column(Integer, ForeignKey('companies_sec.id'),
                             nullable=True)
    partner_two_ous_id = Column(Integer, ForeignKey('companies_ous.id'),
                             nullable=True)
    deal_value = Column(DECIMAL(13, 2), nullable=True)
    type = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
