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


class ClaimChallengedModel(Base):
    __tablename__ = 'claims_challenged'

    id = Column(Integer, primary_key=True)
    ptab2_proceeding_id = Column(
        Integer,
        ForeignKey('ptab2_proceedings.id'),
        nullable=False,
    )
    claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    prior_art_combination = Column(
        Integer,
        nullable=False,
    )
    prior_art_id = Column(
        Integer,
        ForeignKey('prior_arts.id'),
        nullable=False,
    )
    prior_art_nature = Column(String(128))
    nature_of_challenge = Column(Text, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
    __table_args__ = (
        UniqueConstraint(
            'ptab2_proceeding_id',
            'claim_id',
            'prior_art_combination',
            'prior_art_id',
        ),
    )
