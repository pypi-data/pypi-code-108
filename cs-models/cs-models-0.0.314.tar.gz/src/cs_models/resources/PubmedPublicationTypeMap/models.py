from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    Boolean,
)

from ...database import Base


class PubmedPublicationTypeMapModel(Base):
    __tablename__ = "pubmed_publication_type_map"

    id = Column(Integer, primary_key=True)
    pubmed_id = Column(
        Integer,
        ForeignKey('pubmed.id'),
        nullable=False,
    )
    publication_type_id = Column(
        Integer,
        ForeignKey('pubmed_publication_types.id'),
        nullable=False,
    )
    processed = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("pubmed_id", "publication_type_id"),)
