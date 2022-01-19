from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class SubsidiarySponsorMappingModel(Base):
    __tablename__ = 'subsidiary_sponsor_mappings'

    id = Column(Integer, primary_key=True)
    sponsor_id = Column(Integer, nullable=False)
    sponsor_name = Column(String(128), nullable=False)
    lead_or_collaborator = Column(String(50))
    subsidiary_id = Column(
        Integer,
        ForeignKey('subsidiaries.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('sponsor_id', 'subsidiary_id'),)
