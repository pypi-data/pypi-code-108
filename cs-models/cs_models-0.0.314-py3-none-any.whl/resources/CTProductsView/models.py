from sqlalchemy import (
    Integer,
    Column,
    String,
    ForeignKey,
    DateTime,
    Text,
)
from datetime import datetime
from ...database import Base


class CTProductsViewModel(Base):
    __tablename__ = "ct_products_view"

    id = Column(Integer, primary_key=True)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    news_date = Column(DateTime)
    intervention_name = Column(Text)
    nct_id = Column(Text)
    brief_title = Column(Text)
    study_status = Column(String(128))
    study_start_date = Column(DateTime)
    phase = Column(Text)
    company = Column(Text)
    sponsors = Column(Text)
    pharm_action = Column(Text)
    intervention_type = Column(Text)
    conditions = Column(Text)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
