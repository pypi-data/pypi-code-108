from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    Text,
    Boolean,
)
from datetime import datetime
from ...database import Base


class NCTStudyModel(Base):
    __tablename__ = "nct_study"

    id = Column(Integer, primary_key=True)
    nct_id = Column(String(128), nullable=False, unique=True)
    brief_title = Column(Text)
    study_status = Column(String(128))
    study_type = Column(String(50))
    study_start_date = Column(DateTime)
    last_update_submitted_qc_date = Column(DateTime)
    phase = Column(Text)
    sponsors = Column(Text)
    conditions = Column(Text)
    industry_flag = Column(Boolean)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
