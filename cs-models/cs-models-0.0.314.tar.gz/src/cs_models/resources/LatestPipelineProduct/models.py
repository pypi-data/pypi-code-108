from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    ForeignKey,
)

from ...database import Base


class LatestPipelineProductModel(Base):
    __tablename__ = "latest_pipeline_products"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(191), nullable=False, index=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    latest_catalyst_date = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("product_name"),)
