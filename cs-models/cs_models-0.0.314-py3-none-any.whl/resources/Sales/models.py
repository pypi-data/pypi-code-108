from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
    ForeignKey,
)

from ...database import Base


class SalesModel(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    sec_filing_id = Column(
        Integer,
        ForeignKey('companies_sec_filings.id'),
        nullable=False,
    )
    table_html_file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=False,
    )
    table_number = Column(Integer, nullable=False)
    table_preceding_info = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

