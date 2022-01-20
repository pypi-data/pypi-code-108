from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class PharmActionModel(Base):
    __tablename__ = "pharm_actions"

    id = Column(Integer, primary_key=True)
    pharm_action_id = Column(String(128), nullable=False)
    pharm_action = Column(Text, nullable=False)
    pharm_action_type = Column(String(50), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("pharm_action_id"),)
