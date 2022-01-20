from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from ...database import Base


class NDCModel(Base):
    __tablename__ = "ndc"

    id = Column(Integer, primary_key=True)
    spl_id = Column(String(128), nullable=False)
    appl_no = Column(String(10), nullable=False)
    appl_type = Column(String(50), nullable=False)
    spl_set_id = Column(String(128), nullable=True)
    product_ndc = Column(String(128), nullable=True, index=True)
    package_ndc = Column(String(128), nullable=True, index=True)
    route = Column(String(128), nullable=True, index=True)
    dosage_form = Column(String(128), nullable=True)
    generic_name = Column(String(191), nullable=True)
    labeler_name = Column(String(256), nullable=True)
    labeler_subsidiary_id = Column(
        Integer, ForeignKey("subsidiaries.id"), nullable=True,
    )
    brand_name = Column(String(191), nullable=True)
    marketing_category = Column(String(128), nullable=True)
    marketing_start_date = Column(DateTime, nullable=True)
    marketing_end_date = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
