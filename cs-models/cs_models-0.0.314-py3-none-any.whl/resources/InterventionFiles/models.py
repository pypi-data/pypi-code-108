from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    Boolean,
)

from ...database import Base


class InterventionFileModel(Base):
    __tablename__ = "intervention_files"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=False,
    )
    type = Column(String(255), nullable=False)
    orig_file_url = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("intervention_id", "file_id"),)
