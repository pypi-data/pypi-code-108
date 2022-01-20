from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime
from ...database import Base


class PriorArtModel(Base):
    __tablename__ = 'prior_arts'

    id = Column(Integer, primary_key=True)
    ptab2_document_id = Column(
        Integer,
        ForeignKey('ptab2_documents.id'),
    )
    tag = Column(String(128), nullable=False)
    title = Column(Text)
    exhibit = Column(String(128))
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint('ptab2_document_id', 'tag'),)
