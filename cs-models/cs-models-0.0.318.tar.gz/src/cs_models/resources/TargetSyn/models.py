from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class TargetSynModel(Base):
    __tablename__ = 'target_syns'

    id = Column(Integer, primary_key=True)
    synonym = Column(String(191), nullable=False, index=True)
    target_id = Column(
        Integer,
        ForeignKey('targets.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
