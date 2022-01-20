from sqlalchemy import (
    Column,
    String,
)

from ...database import Base


class NDCSetIDCrossModel(Base):
    __tablename__ = "ndc_set_id"

    product_ndc = Column(String(50), nullable=True, primary_key=True)
    package_ndc = Column(String(4000), nullable=True)
    spl_set_id = Column(String(4000), nullable=True, index=True)
