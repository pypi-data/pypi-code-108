from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

from ...database import Base


class StreamModel(Base):
    __tablename__ = "stream"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    resource_type = Column(String(128), nullable=False)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=True,
    )
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=True,
    )
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
    ptab2_proceeding_id = Column(
        Integer,
        ForeignKey('ptab2_proceedings.id'),
        nullable=True,
    )
    source_table = Column(String(50), nullable=False)
    source_table_id = Column(Integer, nullable=False)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    sec_filing_id = Column(
        Integer,
        ForeignKey('companies_sec_filings.id'),
        nullable=True,
    )
    ptab2_document_id = Column(
        Integer,
        ForeignKey('ptab2_documents.id'),
        nullable=True,
    )
    pubmed_id = Column(
        Integer,
        ForeignKey('pubmed.id'),
        nullable=True,
    )
    company_filing_id = Column(
        Integer,
        ForeignKey('company_filings.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
