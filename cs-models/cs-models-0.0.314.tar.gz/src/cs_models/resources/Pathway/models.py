from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from datetime import datetime

from ...database import Base


class PathwayModel(Base):
    __tablename__ = 'pathways'

    id = Column(Integer, primary_key=True)
    reactome_pathway_id = Column(String(50), unique=True, nullable=False)
    reactome_pathway_name = Column(String(191), nullable=False)
    reactome_pathway_type = Column(String(50), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
