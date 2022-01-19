from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)
from datetime import datetime

from ...database import Base


class CompanyFilingModel(Base):
    __tablename__ = 'company_filings'

    id = Column(Integer, primary_key=True)
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
    file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=False,
    )
    date = Column(DateTime, nullable=True)
    title = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)
    orig_file_url = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    unprocessed = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
