from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
)

from ...database import Base


class TableOutboxModel(Base):
    __tablename__ = "table_outbox"

    id = Column(Integer, primary_key=True)
    sec_filing_id = Column(Integer, nullable=False)
    table_html = Column(Text, nullable=False)
    table_number = Column(Integer, nullable=False)
    table_preceding_info = Column(Text, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
