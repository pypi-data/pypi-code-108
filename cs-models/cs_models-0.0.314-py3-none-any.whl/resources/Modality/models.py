from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from datetime import datetime

from ...database import Base


class ModalityModel(Base):
    __tablename__ = 'modalities'

    id = Column(Integer, primary_key=True)
    modality = Column(String(50), unique=True, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
