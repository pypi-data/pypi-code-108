from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class ConfigModel(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    table_name = Column(String(128), nullable=False)
    field_name = Column(String(128), nullable=False)
    latest_date = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('table_name', 'field_name'),)
