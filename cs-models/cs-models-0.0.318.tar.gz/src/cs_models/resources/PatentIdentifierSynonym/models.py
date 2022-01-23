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


class PatentIdentifierSynonymModel(Base):
    __tablename__ = 'patent_identifier_synonyms'

    id = Column(Integer, primary_key=True)
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
        nullable=False,
    )
    synonym = Column(String(128), nullable=False)

    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
    __table_args__ = (UniqueConstraint('patent_id', 'synonym'),)
