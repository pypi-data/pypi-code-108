from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from ...database import Base


class OrangeBookProductModel(Base):
    __tablename__ = "orange_book_products"

    id = Column(Integer, primary_key=True)
    appl_no = Column(String(256), index=True)
    appl_type = Column(String(256), index=True)
    applicant = Column(String(256))
    applicant_full_name = Column(String(191))
    applicant_subsidiary_id = Column(
        Integer, ForeignKey("subsidiaries.id"), nullable=True,
    )
    approval_date = Column(DateTime)
    dosage_form = Column(String(256))
    ingredient = Column(String(256))
    product_no = Column(String(128))
    rld = Column(String(256))
    rs = Column(String(256))
    route_of_administration = Column(String(256))
    strength = Column(String(500))
    te_code = Column(String(256))
    trade_name = Column(String(256), index=True)
    type = Column(String(256))
    drug_set_id = Column(String(128), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

