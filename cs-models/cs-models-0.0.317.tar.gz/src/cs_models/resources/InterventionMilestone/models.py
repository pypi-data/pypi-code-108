from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    String,
    Text,
)

from ...database import Base


class InterventionMilestoneModel(Base):
    __tablename__ = "intervention_milestones"

    id = Column(Integer, primary_key=True)
    intervention_condition_id = Column(
        Integer,
        ForeignKey('intervention_condition.id'),
        nullable=False,
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    milestone = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    source_url = Column(String(255), nullable=True)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    sec_filing_id = Column(
        Integer,
        ForeignKey('companies_sec_filings.id'),
        nullable=True,
    )
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
