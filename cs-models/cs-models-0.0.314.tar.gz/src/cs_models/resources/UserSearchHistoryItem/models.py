from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from datetime import datetime

from ...database import Base


class UserSearchHistoryItemModel(Base):
    __tablename__ = 'user_search_history_items'

    id = Column(Integer, primary_key=True)

    user_id = Column(String(128), nullable=False)
    search_term = Column(String(255), nullable=False)
    search_type = Column(String(255))

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
