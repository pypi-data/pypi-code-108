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


class WatchlistModel(Base):
    __tablename__ = 'watchlists'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False)
    resource_type = Column(String(128), nullable=False)
    norm_cui = Column(String(50), nullable=True, index=True)
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
    is_active = Column(Boolean, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
