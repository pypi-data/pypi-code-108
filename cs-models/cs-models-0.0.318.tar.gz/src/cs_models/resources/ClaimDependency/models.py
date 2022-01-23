from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class ClaimDependencyModel(Base):
    __tablename__ = 'claim_dependencies'

    id = Column(Integer, primary_key=True)
    claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    parent_claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
