from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from ...database import Base


class FederalCaseRefModel(Base):
    __tablename__ = "federal_case_refs"

    id = Column(Integer, primary_key=True)
    case_name = Column(String(128), nullable=False)
    volume = Column(Integer, nullable=False)
    reporter_type = Column(String(50), nullable=False)
    page = Column(Integer, nullable=False)
    title = Column(String(128), nullable=False)
    link = Column(String(128), nullable=False)
    federal_case_file_id = Column(Integer, ForeignKey("files.id"))

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
