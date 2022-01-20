from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    String,
)

from ...database import Base


class RegulatoryApprovalOutboxModel(Base):
    __tablename__ = "regulatory_approval_outbox"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=False,
    )
    approval_text = Column(Text, nullable=False)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=True,
    )
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=True,
    )
    geography = Column(String(50), nullable=True)
    stage = Column(Integer, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
