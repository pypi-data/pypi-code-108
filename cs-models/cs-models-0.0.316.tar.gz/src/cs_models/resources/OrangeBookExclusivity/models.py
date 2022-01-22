from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class OrangeBookExclusivityModel(Base):
    __tablename__ = 'orange_book_exclusivities'

    id = Column(Integer, primary_key=True)
    appl_no = Column(String(128), nullable=False)
    appl_type = Column(String(128), nullable=False)
    product_no = Column(String(128), nullable=False)
    exclusivity_code = Column(String(128), nullable=False)
    exclusivity_date = Column(DateTime)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint(
        'appl_type', 'appl_no', 'product_no', 'exclusivity_code'),)
