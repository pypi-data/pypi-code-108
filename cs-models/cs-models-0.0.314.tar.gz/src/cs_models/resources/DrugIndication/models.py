from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
)

from ...database import Base


class DrugIndicationModel(Base):
    __tablename__ = "drug_indications"

    id = Column(Integer, primary_key=True)
    set_id = Column(String(128), nullable=False, index=True)
    lowercase_indication = Column(String(128), nullable=True)
    indication = Column(Text, nullable=True)
    label_file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
