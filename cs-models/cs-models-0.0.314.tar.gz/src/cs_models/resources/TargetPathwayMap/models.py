from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
)
from datetime import datetime

from ...database import Base


class TargetPathwayMapModel(Base):
    __tablename__ = 'target_pathway_mapping'

    id = Column(Integer, primary_key=True)
    target_id = Column(
        Integer,
        ForeignKey('targets.id'),
        nullable=False,
    )
    pathway_id = Column(
        Integer,
        ForeignKey('pathways.id'),
        nullable=False,
    )
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
