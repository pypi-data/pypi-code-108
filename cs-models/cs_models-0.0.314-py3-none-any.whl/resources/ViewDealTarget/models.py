from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class ViewDealTargetModel(Base):
    __tablename__ = "_view_deal_targets"

    id = Column(Integer, primary_key=True)
    deal_id = Column(
        Integer,
        ForeignKey('deals.id'),
        nullable=False,
    )
    target_id = Column(
        Integer,
        ForeignKey('targets.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
