from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class CompanyOutboxModel(Base):
    __tablename__ = 'company_outbox'

    id = Column(Integer, primary_key=True)
    cik_str = Column(String(128), nullable=True)
    ticker = Column(String(20), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    exchange = Column(String(50), nullable=True)
    company_sec_id = Column(
        Integer,
        ForeignKey('companies_sec.id'),
        nullable=True,
    )
    company_ous_id = Column(
        Integer,
        ForeignKey('companies_ous.id'),
        nullable=True,
    )
    source = Column(String(50), nullable=False)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

