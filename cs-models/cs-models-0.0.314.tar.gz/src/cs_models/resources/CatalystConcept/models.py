from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)

from ...database import Base


class CatalystConceptModel(Base):
    __tablename__ = "catalyst_concepts"

    id = Column(Integer, primary_key=True)
    concept_name = Column(String(128), nullable=False, index=True)
    relation = Column(String(128), nullable=False)
    property = Column(Text, nullable=False)
    news_id = Column(
        Integer,
        ForeignKey('newswires.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
