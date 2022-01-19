from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from ...database import Base


class DocumentReferenceModel(Base):
    __tablename__ = "document_references"

    id = Column(Integer, primary_key=True)
    ptab2_document_id = Column(
        Integer, ForeignKey("ptab2_documents.id"), nullable=False,
    )
    type = Column(String(50), nullable=False)
    value = Column(String(128), nullable=False)
    federal_case_headline = Column(String(256))
    federal_case_number = Column(String(256), index=True)
    link = Column(String(500))
    federal_case_file_id = Column(Integer, ForeignKey("files.id"))
    pages = Column(Text)

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint("ptab2_document_id", "type", "value"),)
