from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class CompanySECFilingModel(Base):
    __tablename__ = 'companies_sec_filings'

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
    cik_str = Column(String(128), nullable=True)
    sec_form_header = Column(String(50))
    sec_filing_date = Column(DateTime)
    sec_accession_number = Column(String(128))
    sec_index_url = Column(String(128))
    sec_url = Column(String(128))
    document_group = Column(String(50), nullable=True)
    section_name = Column(String(50), nullable=True)
    extraction_method = Column(String(50), nullable=True)
    excerpt_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    source_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('sec_accession_number', 'document_group', 'section_name'),)
