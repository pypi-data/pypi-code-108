from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class ProceedingStageModel(Base):
    __tablename__ = 'proceeding_stages'

    id = Column(Integer, primary_key=True)
    ptab2_proceeding_id = Column(
        Integer,
        ForeignKey('ptab2_proceedings.id'),
        nullable=False,
    )
    stage = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False)
    filed_date = Column(DateTime)
    due_date = Column(DateTime)
    file_id = Column(Integer, ForeignKey("files.id"))
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('ptab2_proceeding_id', 'stage'),)
