from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from datetime import datetime

from ...database import Base


class CompanyOUSModel(Base):
    __tablename__ = 'companies_ous'

    id = Column(Integer, primary_key=True)
    cik = Column(Integer, index=True, nullable=True)
    name = Column(String(190), unique=True, nullable=False)
    ticker = Column(String(20), nullable=True, index=True)
    exchange = Column(String(100), nullable=True)
    company_url = Column(String(255), nullable=True)
    pipeline_url = Column(String(255), nullable=True)
    ir_url = Column(String(255), nullable=True)
    is_activated = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
