from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    String,
)

from ...database import Base


class SalesProductsMapModel(Base):
    __tablename__ = "sales_products_map"

    id = Column(Integer, primary_key=True)
    sales_table_id = Column(
        Integer,
        ForeignKey('sales.id'),
        nullable=False,
    )
    product_name = Column(String(191), nullable=False)
    source = Column(String(20), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("sales_table_id", "product_name"),)
