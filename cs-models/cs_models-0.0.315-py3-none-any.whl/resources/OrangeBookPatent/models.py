from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from ...database import Base


class OrangeBookPatentModel(Base):
    __tablename__ = 'orange_book_patents'

    id = Column(Integer, primary_key=True)
    appl_no = Column(String(128), index=True)
    appl_type = Column(String(128), nullable=False, index=True)
    delist_flag = Column(String(128))
    drug_product_flag = Column(String(128))
    drug_substance_flag = Column(String(128))
    patent_no = Column(String(128), nullable=False, index=True)
    patent_use_code = Column(String(128), nullable=False)
    product_no = Column(String(128), nullable=False)
    patent_expire_date = Column(DateTime)
    submission_date = Column(DateTime)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
