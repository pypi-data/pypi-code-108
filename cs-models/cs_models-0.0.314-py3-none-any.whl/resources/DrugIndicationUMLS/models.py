from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)

from ...database import Base


class DrugIndicationUMLSModel(Base):
    __tablename__ = "drug_indications_umls"

    id = Column(Integer, primary_key=True)
    set_id = Column(String(128), nullable=False, index=True)
    cui = Column(String(50), nullable=False)
    preferred_name = Column(String(128), nullable=True)
    score = Column(Integer, nullable=True)
    final_mapping = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
