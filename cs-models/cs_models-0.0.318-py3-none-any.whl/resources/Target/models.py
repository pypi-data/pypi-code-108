from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from datetime import datetime

from ...database import Base


class TargetModel(Base):
    __tablename__ = 'targets'

    id = Column(Integer, primary_key=True)

    cui = Column(String(50), unique=True, nullable=False)
    name = Column(String(191), nullable=False)
    symbol = Column(String(50), nullable=False)
    bio_type = Column(String(191), nullable=True)
    pathways = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
